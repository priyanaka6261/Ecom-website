from django.shortcuts import render , redirect
from .models import User , Product , Wishlist , Cart
import stripe
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
#for sending otp in email
from django.conf import settings
from django.core.mail import send_mail
import random
#for AJAX
from django.http import JsonResponse


def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="buyer":
			product=Product.objects.all()
			carts=Cart.objects.filter(user=user)
			
			return render(request,'index.html',{'product':product,'carts':carts})

		else:
			seller=User.objects.get(email=request.session['email'])
			products=Product.objects.filter(seller=seller)
			return render(request,'seller-index.html',{"products":products})

	except:
		product=Product.objects.all()
		return render(request,'index.html',{'product':product})
		

def seller_index(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,'seller-index.html',{'products':products})

def signup(request):
	if request.method=='POST':
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})

		except:
			if request.POST['password']==request.POST['cpassword']:

				User.objects.create(
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						usertype=request.POST['usertype'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						profile_pic=request.FILES['profile_pic'],
														
					)

				msg="User Registered successfully"
				return render(request,"signup.html",{'msg':msg})
			else:
				msg="Password and confirm password doesn't matched"
				return render(request,"signup.html",{'msg':msg})


	else:
		return render(request,'signup.html')

# Function to Validate Email using AJAX

def validate_signup(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)

def validate_mobile(request):
	mobile=request.GET.get('mobile')
	data={
		'is_taken':User.objects.filter(mobile__iexact=mobile).exists()
	}
	return JsonResponse(data)

def login(request):
	try:
		user=User.objects.get(email=request.POST['email'])
		if user.password==request.POST['password']:
			if user.usertype=="buyer":
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				wishlists=Wishlist.objects.filter(user=user)
				request.session['wishlist_count']=len(wishlists)
				carts=Cart.objects.filter(user=user)				
				request.session['cart_count']=len(carts)
				return redirect('index')

			else:
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				return redirect('seller-index')

		else:
			msg="Incorrect Password"
			return render(request,'login.html',{'msg':msg})
	except:
		msg="Email not Registered"
		return render(request,'login.html',{'msg':msg})



	return render(request,'login.html')

def logout(request):

	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_pic']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=random.randint(1000,9999)			
			#for sending mail
			subject = "OTP for Forgot Password"
			message = "Hello"+user.fname+", Your OTP for Forgot Password is "+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'email':user.email,'otp':otp})
		except:
			msg="Email not Registered"
			return render(request,'forgot-password.html',{'msg':msg})


def change_password(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				if user.usertype=="buyer":
					carts=Cart.objects.filter(user=user)
					msg="New password and Confirm new password doesn't matched"
					return render(request,"change-password.html",{'msg':msg,'carts':carts})

				else:
					msg="New password and Confirm new password doesn't matched"
					return render(request,"seller-change-password.html",{'msg':msg})
		else:
			if user.usertype=="buyer":
				carts=Cart.objects.filter(user=user)
				msg="Old password doesn't matched"
				return render(request,"change-password.html",{'msg':msg,'carts':carts})
			else:
				msg="Old password doesn't matched"
				return render(request,"seller-change-password.html",{'msg':msg})

	else:
		if user.usertype=="buyer":
			return render(request,"change-password.html")
		else:
			return render(request,"seller-change-password.html")


def validate_change_password(request):
	old_password=request.GET.get('old_password')
	data={
		'is_taken':User.objects.filter(password__iexact='old_password').exists()
	}
	return JsonResponse(data)

def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_pic=request.FILES['profile_pic']

		except:
			pass
		user.save()
		request.session['profile_pic']=user.profile_pic.url
		msg="Profile Updated Successfully"
		if user.usertype=="buyer":
			carts=Cart.objects.filter(user=user)
			return render(request,'profile.html',{'user':user,"msg":msg,'carts':carts})
		else:
			return render(request,'seller-profile.html',{'user':user,'msg':msg})
	else:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="buyer":
			carts=Cart.objects.filter(user=user)
			return render(request,'profile.html',{'user':user,'carts':carts})
		else:
			return render(request,'seller-profile.html',{'user':user})



def seller_add_product(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
				seller=seller,
				product_category=request.POST['product_category'],
				product_name=request.POST['product_name'],
				product_desc=request.POST['product_desc'],
				product_price=request.POST['product_price'],
				product_image=request.FILES['product_image']

			)
		msg="Product Added Successfully"
		return render(request,'seller-add-product.html',{'msg':msg})
	else:
		return render(request,'seller-add-product.html')

def validate_product_name(request):
	product_name=request.GET.get('product_name')
	data={
		'is_taken':Product.objects.filter(product_name__iexact=product_name).exists()
	}
	return JsonResponse(data)

def seller_view_product(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,"seller-view-product.html",{'products':products})


def seller_product_details(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller-product-details.html',{'product':product})


def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_category=request.POST['product_category']
		product.product_name=request.POST['product_name']
		product.product_desc=request.POST['product_desc']
		product.product_price=request.POST['product_price']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		msg="Product Updated Successfully"
		return render(request,'seller-edit-product.html',{'product':product,'msg':msg})

	else:
		return render(request,'seller-edit-product.html',{'product':product})


def seller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller-view-product')


def men(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	product=Product.objects.filter(product_category="Men")
	return render(request,'index.html',{"product":product,'carts':carts})

def women(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	product=Product.objects.filter(product_category="Women")
	return render(request,'index.html',{"product":product,'carts':carts})

def product_details(request,pk):
	wishlist_flag = False
	cart_flag = False
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	product=Product.objects.get(pk=pk)
	try:

		Wishlist.objects.get(user=user,product=product)
		wishlist_flag = True

	except:
		pass

	try:

		Cart.objects.get(user=user,product=product)
		cart_flag = True

	except:
		pass


	return render(request,'product-details.html',{"product":product,"wishlist_flag":wishlist_flag,'cart_flag':cart_flag,'carts':carts})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	product.wishlist_status=True
	product.save()
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,product=product)
	return redirect('wishlist')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	wishlist=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlist)
	return render(request,'wishlist.html',{'wishlist':wishlist,'carts':carts})


def remove_from_wishlist(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	product.wishlist_status=False
	product.save()
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')


def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	# for getting net price in cart
	for i in carts:
		net_price += i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts , 'net_price':net_price})



def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	product.cart_status=True
	product.save()
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(
		user=user,
		product=product,
		product_price=product.product_price,
		product_qty=1,
		total_price=product.product_price
		)
	return redirect('cart')

def remove_from_cart(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	product.cart_status=False
	product.save()
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def checkout(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.filter(user=user)
	for i in cart:
		net_price += i.total_price
	return render(request,'checkout.html',{'user':user,'cart':cart,'net_price':net_price})

#Payment Integration
stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'

@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100
	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'product_data': {
					'name': 'Intro to Django Course',
					},
				'unit_amount': final_amount,
				},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',)
	return JsonResponse({'id': session.id})

def success(request):
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')