from django.shortcuts import render,redirect
from courses.models import Course,Video,Payment,UserCourse,CouponCode
from courses.forms import registrationForm,loginForm
from django.views import View
from django.http import HttpResponse
from django.contrib.auth import logout
from onlinecourses.settings import *
from time import time
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
# Create your views here.

import razorpay
client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))



def sample(request):
	course=Course.objects.all()
	return render(request,"courses/home.html",{'courses':course})


# course page

def coursePage(request,slugs):
	course=Course.objects.get(slugs=slugs)
	serial=request.GET.get('lecture')
	if serial is None:
		serial=1
	#print(serial)
	video=Video.objects.get(serial_number=serial,course=course)
	videos=course.video_set.all().order_by("serial_number")
	if video.is_preview is False:
		if request.user.is_authenticated is False: 
			return redirect('login')
		else:
			user=request.user
			try:
				user_course=UserCourse.objects.get(user=user,course=course)
			except:
				return redirect('checkout',slugs=course.slugs)
	return render(request,'courses/coursepage.html',{'course':course,'video':video,'videos':videos})
		

#signup

class signup(View):
	def get(self,request):
		form=registrationForm()
		return render(request,"courses/signup.html",{'form':form})
	def post(self,request):
		form=registrationForm(request.POST)
		if(form.is_valid()):
			user=form.save()
			if user:
				return redirect('login')
		return render(request,"courses/signup.html",{"form":form})


#login

class login(View):
	def get(self,request):
		form=loginForm()
		return render(request,'courses/login.html',{'form':form})
	def post(self,request):
		form=loginForm(request=request,data=request.POST)
		if form.is_valid():
			return redirect('home')
		return render(request,'courses/login.html',{'form':form})

#logout

def signout(request):
	logout(request)
	return redirect("home")


#checkout

def checkout(request,slugs):
	course=Course.objects.get(slugs=slugs)
	user=None
	order=None
	payment=None
	couponmsg=""
	coupon=None
	if not request.user.is_authenticated: 
		return redirect('login')
	else:
		user=request.user
		action=request.GET.get('action')
		couponcode=request.GET.get('couponcode')		
		error=None
		amount=None
		try:
			user_course=UserCourse.objects.get(user=user,course=course)
			error="You already Purchased this Course"
		except:
			pass
		if error is None:
			amount=int((course.price-(course.price*course.discount*0.01))*100)
		if couponcode:
			try:
				coupon=CouponCode.objects.get(course=course,code=couponcode)
				amount=int((course.price*coupon.discount*0.01)*100)
				couponmsg="CouponCode Applied"
			except:
				couponmsg="Invalid Coupon"

		if amount == 0:
			user_course=UserCourse(user=user,course=course)
			user_course.save()
			course=Course.objects.all()
			return redirect("/")
		

		if action=='create_payment':
				
			currency="INR"
			receipt=f"onlinecourse-{int(time())}"
			notes = {
					"email": user.email,
					"name": f'{user.first_name} {user.last_name}'
			}
			#print(type(Notes))
			order=client.order.create({
				'receipt':receipt,
				'amount':amount,
				'currency':currency,
				'notes': notes
				})
			#print("error")
			payment=Payment()
			payment.user=user
			payment.course=course
			payment.order_id=order.get('id')
			payment.save()
	
	
	context={
			'course':course,
			'error':error,
			'order':order,
			'payment':payment,
			'user':user,
			'couponmsg':couponmsg,
			'coupon':coupon
			}

	return render(request,'courses/checkout.html',context=context)
		


@csrf_exempt
def verify_payment(request):
	if request.method=="POST":
		data=request.POST
		context={}
		try:
			client.utility.verify_payment_signature(data)
			razorpay_order_id=data['razorpay_order_id']
			razorpay_payment_id=data['razorpay_payment_id']
			#print("Razor")
			payment=Payment.objects.get(order_id=razorpay_order_id)
			payment.payment_id=razorpay_payment_id
			payment.status=True	
			userCourse=UserCourse(user=payment.user,course=payment.course)
			userCourse.save()

			payment.user_course=userCourse
			payment.save()	
			context={
				'payment':payment
			}
			return render(request,"courses/test.html",context=context)
		except:
			
			return render(request,'courses/test.html')

		
	return redirect('home')



#my course
@login_required(login_url="login")
def my_course(request):
	user=request.user
	course=UserCourse.objects.filter(user=user)
	context={
		'user_course':course,
	}
	return render(request,"courses/my_course.html",context=context)