from ast import Sub
from asyncio.windows_events import NULL
from genericpath import exists
from django.views import generic
from django.shortcuts import  render, redirect,get_object_or_404
from .forms import NewUserForm,AuthenticationForm,ContactForm
from django.contrib.auth import login, authenticate,logout
from django.conf import settings
from WEB_BASED_BIKE_SHARING_APPLICATION import settings
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
import random,simplejson,stripe,qrcode
from .models import DockStation,UserOTP,Booking,StripeCustomer,StripePasses,userhasbike,user_booking_history
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib import messages
from geopy.geocoders import Nominatim
from geopy.distance import  great_circle
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.template.defaulttags import register
from qrcode import *



now = datetime.now()
current_time = now.strftime("%H:%M")

# Create your views here.

@csrf_protect
def homepage(request):
    location_list = list(DockStation.objects.order_by('name').values()) 
    location_json = simplejson.dumps(location_list,use_decimal = True)  
    TOM_TOM_MAPS_API_KEY = simplejson.dumps(settings.TOM_TOM_MAPS_API_KEY)

    context = {'locations': location_json,'TOM_TOM_MAPS_API_KEY':TOM_TOM_MAPS_API_KEY} 
    return render(request, 'main/home.html', context) 


@csrf_protect
def register_request(request):
    if request.method == 'POST':
        get_otp = request.POST.get('otp') #213243 #None
        if get_otp:
            get_usr = request.POST.get('usr')
            usr = User.objects.get(username=get_usr)
            if int(get_otp) == UserOTP.objects.filter(user = usr).last().otp:
                usr.is_active = True		
                usr.save()
                messages.success(request, f'Account is Created For {usr.username}')
                return redirect('main:signin')
            else:
                messages.warning(request, f'You Entered a Wrong OTP')
                return render(request, 'main/register.html', {'otp': True, 'usr': usr})
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            usr = User.objects.get(username=username)
            usr.email = email
            usr.username = username
            usr.is_active = False
            usr.save()
            usr_otp = random.randint(100000, 999999)
            UserOTP.objects.create(user = usr, otp = usr_otp)
            message = f"Hello {usr.username}\n\nTo authenticate, please enter the following one time password:\n {usr_otp} \n Thanks!"
            send_mail("Welcome to Bikers Hub - Verify Your Email",message,settings.EMAIL_HOST_USER,[usr.email],fail_silently = False)
            return render(request, 'main/register.html', {'otp': True, 'usr': usr})		
    else:
        form = NewUserForm()
    return render(request, 'main/register.html', {'register_form':form})




def signin_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("main:homepage")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="main/signin.html", context={"login_form":form})


@csrf_protect
def logout_request(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("main:homepage")

@csrf_protect
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "main/password/password_reset_email.txt"
                    c = {
                    "email":user.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Website',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
                    except BadHeaderError:

                        return HttpResponse('Invalid header found.')
                        
                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                    return redirect ("main:homepage")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="main/password/password_reset.html", context={"password_reset_form":password_reset_form})

@csrf_protect
def contact_us(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Contact form inquiry"
            body={
                'subject' : form.cleaned_data['subject'],
                'from_email' : form.cleaned_data['from_email'],
                'message' : form.cleaned_data['message'],
            }
            message = '\n'.join('='.join((key,val)) for (key,val) in body.items())
            sender = form.cleaned_data['from_email']
            recipient = ['bikers.den.official@gmail.com']
            try:
                send_mail(subject, message, sender,recipient,fail_silently=True)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('main:success')
    return render(request, "main/contact.html", {'form': form})

@csrf_protect
def successView(request):
    return render(request,'main/success.html')

@csrf_protect
def postcodesearch(request):
    
    return render(request,'main/postcodesearch.html')

@csrf_protect
def search(request):
    DockStation_objects = DockStation.objects.all()
    postcode = request.GET.get('postcode')
    mile_radius = request.GET.get('mile_radius')
    user_latitude = None
    user_longitude = None
    if postcode:
        geolocator = Nominatim(user_agent ='main')
        location = geolocator.geocode(postcode)
        user_latitude = location.latitude
        user_longitude = location.longitude
    output = []
    for DockStation_object in DockStation_objects:
            result = {}
            result['name'] = DockStation_object.name
            result['image'] = DockStation_object.image
            result['landmark'] = DockStation_object.landmark
            result['postcode'] = DockStation_object.postcode
            result['address'] = DockStation_object.address
            result['total_docks']=DockStation_object.total_docks
            result['bikes_availible']=DockStation_object.bikes_availible
            result['dropoff_docks']=DockStation_object.dropoff_docks
            result['id'] = DockStation_object.id
            result['url'] = '127.0.0.1:8000/bikeavailibility/' + str(DockStation_object.id)
            if postcode:
                initial_coords = (float(user_latitude),float(user_longitude))
                station_coords = (float(DockStation_object.latitude), float(DockStation_object.longitude))
                result['distance'] = round(great_circle(initial_coords,station_coords).miles,3)
            output.append(result)
            output = sorted(output,key=lambda d:d['distance']) 
            if mile_radius:
                if result['distance'] > float(mile_radius):
                    output.pop()
    return JsonResponse(output,safe=False)


@csrf_protect
def bikeavailibility(request,id):
    user = User.objects.get(username = request.user)
    stripecustomer = StripeCustomer.objects.filter(user = user)

    if stripecustomer:
        obj = get_object_or_404(DockStation,pk = id)
        stripe_customer = StripeCustomer.objects.get(user=request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
        context = {'obj':obj,'subscription':subscription}
        return render(request,'main/bikeavailibility.html',context)
    else:
        obj = get_object_or_404(DockStation,pk = id)
        context = {'obj':obj}
        return render(request,'main/bikeavailibility.html',context)

@register.filter(name='booking_id')
def booking_id(user):
    if Booking.objects.filter(bicycle_drop_status=False).filter(user=user).exists():
        ins=Booking.objects.get(bicycle_drop_status=False,user=user)
    return ins.id

@csrf_protect
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)
@method_decorator(login_required(login_url='/'), name='dispatch')	
class BookingView(generic.TemplateView):
    template_name = 'main/bookings.html'
    STRIPE_PUBLISHABLE_KEY = simplejson.dumps(settings.STRIPE_PUBLISHABLE_KEY)
    

    def get(self,request,id):
        instance=DockStation.objects.get(id=id)
        address= DockStation.objects.values_list('address',flat=True)	
        pass_type= StripePasses.objects.values_list('pass_name',flat=True)  
        bikes_availible=instance.bikes_availible
        STRIPE_PUBLISHABLE_KEY = simplejson.dumps(settings.STRIPE_PUBLISHABLE_KEY)

        return render(request,self.template_name,{'current_time':current_time,
      'instance':instance,'address':address,'bikes_availible':bikes_availible,'pass_type':pass_type,'STRIPE_PUBLISHABLE_KEY':STRIPE_PUBLISHABLE_KEY})

@csrf_protect
def create_checkout_session(request):
    if request.method == 'POST':               
        email = request.POST.get('email')                      
        booking_to = request.POST.get('booking_to')
        station = DockStation.objects.get(address = booking_to)
        user = User.objects.get(username=request.user)
        if userhasbike.objects.filter(user = user).exists():
            userhasbike.objects.filter(user=user).delete()
        userhasbike.objects.create(user = request.user,has_bike = False)   
        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_session = stripe.checkout.Session.create(
            success_url=request.build_absolute_uri(reverse('main:complete') ) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse('main:cancelled_transaction')),
            client_reference_id=request.user.id if request.user.is_authenticated else None,
            customer_email = email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                }
            ],
            mode='subscription',
        )        
        stripecustomer = userhasbike.objects.get(user = request.user)
        stripecustomer.has_bike = True
        station.bikes_availible = station.bikes_availible -1
        station.dropoff_docks = station.dropoff_docks + 1
        # user_booking_history.objects.create(user = request.user, starting_point = station.address, pass_type = 'Full Day Pass', amount_charged = '4.99' )
        station.save()
        stripecustomer.save()
        return redirect(checkout_session["url"])

qr_data = None
@login_required
def mypass(request):
    global qr_data
    try:
        stripe_customer = StripeCustomer.objects.get(user=request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
        product = stripe.Product.retrieve(subscription.plan.product)
        address1= DockStation.objects.values_list('address',flat=True) 
        availibility = DockStation.objects.values_list('bikes_availible',flat=True)     
        stations = DockStation.objects.all() 
        qr_data = {

            'user' : stripe_customer.user.username,
            'pass':product.name,
            'status' : subscription.status,
        }
        img = make(qr_data,box_size =5.5)
        img.save("main/static/image/qrcode.png")        
        stripe_customer_status = stripe_customer.cancel_at_day_end
        if userhasbike.objects.filter(user = request.user).exists():
            status = userhasbike.objects.get(user = request.user)
            has_bike = status.has_bike 
        return render(request, 'main/mypass.html', {
            'subscription': subscription,
            'product': product,
            'stations':stations,
            'address1':address1,
            'availibility':availibility,
            'has_bike':has_bike,
            'stripe_customer_status' : stripe_customer_status,
            'qr_data':qr_data,
        })
    except StripeCustomer.DoesNotExist:
        return render(request, 'main/mypass.html')


@login_required
def cancel(request):
    try:
        # Retrieve the subscription & product
        stripe_customer = StripeCustomer.objects.get(user=request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
        subscription.cancel_at_period_end = True
        stripe_customer.cancel_at_day_end = True
        subscription.save()
        stripe_customer.save()    
        messages.success(request, f"Reccuring payments cancelled successfully...")
        return render(request,'main/cancel.html')
    except StripeCustomer.DoesNotExist:
        return render(request, 'main/home.html')

@csrf_exempt
def complete(request):
    return render(request, "main/complete.html")



@csrf_exempt
def cancelled_transaction(request):
    return render(request, "main/cancelled_transaction.html")


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    try:
        event = stripe.Webhook.construct_event(
            payload,sig_header,endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Fetch all the required data from session
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')
        payment_intnt_id = session.get('payment_intent')
        # Get the user and create a new StripeCustomer
        user = User.objects.get(id=client_reference_id)
        send_mail(subject='You Bought a Day Pass!', 
                    message=f'Hello {request.user}/n/nThanks for purchasing day pass/n/namount charged:£4.99/n/nPlease note that the day pass is recurring, you can cancel the next day payments anytime under my pass secton/n/nthank you',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently = False
                    )
        if StripeCustomer.objects.filter(user = user).exists():
            StripeCustomer.objects.filter(user=user).update(
            user=user,
            stripeCustomerId=stripe_customer_id,
            stripeSubscriptionId=stripe_subscription_id,
            stripe_payment_intent = payment_intnt_id,
            cancel_at_day_end = False
            )
        StripeCustomer.objects.create(
            user=user,
            stripeCustomerId=stripe_customer_id,
            stripeSubscriptionId=stripe_subscription_id,
            stripe_payment_intent = payment_intnt_id,
            cancel_at_day_end = False
        )

        user_booking_history.objects.create(user = request.user, starting_point = station.address, pass_type = 'Full Day Pass', amount_charged = '4.99' )
        print(user.username + ' just subscribed.')
    return HttpResponse(status=200)


def dropbike(request):
    if request.method == 'POST':
        booking = StripeCustomer.objects.get(user = request.user)
        booking_to = request.POST.get('booking_to')
        station = DockStation.objects.get(address = booking_to)
        output = []
        result = {}
        result['name'] = station.name
        result['image'] = station.image
        result['landmark'] = station.landmark
        result['postcode'] = station.postcode
        result['address'] = station.address
        result['total_docks']=station.total_docks
        result['bikes_availible']=station.bikes_availible
        result['dropoff_docks']=station.dropoff_docks
        result['id'] = station.id
        result['url'] = '127.0.0.1:8000/bikeavailibility/' + str(station.id)
        station.bikes_availible = station.bikes_availible + 1
        station.dropoff_docks = station.dropoff_docks -1
        booking.booking_to = booking_to
        stripecustomer = userhasbike.objects.get(user = request.user)
        stripecustomer.has_bike = False 
        stripecustomer.save()
        station.save()
        output.append(result)
        messages.success(request, f"Bike Succesfully dropped at {booking_to}")
    return redirect("main:homepage")


def pickbike(request):
    if request.method == 'POST':
        booking = StripeCustomer.objects.get(user = request.user)
        booking_to = request.POST.get('booking_to')
        station = DockStation.objects.get(address = booking_to)
        output = []
        result = {}
        result['name'] = station.name
        result['image'] = station.image
        result['landmark'] = station.landmark
        result['postcode'] = station.postcode
        result['address'] = station.address
        result['total_docks']=station.total_docks
        result['bikes_availible']=station.bikes_availible
        result['dropoff_docks']=station.dropoff_docks
        result['id'] = station.id
        result['url'] = '127.0.0.1:8000/bikeavailibility/' + str(station.id)
        station.bikes_availible = station.bikes_availible - 1
        station.dropoff_docks = station.dropoff_docks + 1
        booking.booking_to = booking_to
        stripecustomer = userhasbike.objects.get(user = request.user)
        stripecustomer.has_bike = True
        station.save()
        stripecustomer.save()
        output.append(result)
        messages.success(request, f"Your Request was successfull. You can pick your bike at {booking_to}")
    return redirect("main:homepage")

def user_bookings(request):
    if request.method == 'POST':
    
        bookings = user_booking_history.objects.filter(user= request.user)
        context = {'bookings':bookings}
        output =[]
        for user_bookings in bookings:
            result = {}
            result['starting_point'] = user_bookings.starting_point
            result['pass_type'] = user_bookings.pass_type
            result['amount_charged'] = user_bookings.amount_charged
            output.append(result)
    
    return render(request,"main/user_bookingss.html")


def booking_history(request):
  

    
    bookings = user_booking_history.objects.filter(user= request.user)
    
    return render(request,"main/booking_history.html",{'bookings':bookings})

    


