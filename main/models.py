from asyncio.windows_events import NULL
from django.db import models
from django.contrib.auth.models import User,AbstractUser
from geopy.geocoders import Nominatim
from django.urls import reverse

class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    time_st = models.DateTimeField(auto_now=True)
    otp = models.PositiveSmallIntegerField()


class DockStation(models.Model): 
    affiliate_url = models.SlugField(blank=True, null=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=200) 
    postcode = models.CharField(max_length=100) 
    landmark = models.TextField(blank=True)
    image = models.CharField(max_length=500,null=True)
    total_docks = models.IntegerField()
    bikes_availible = models.IntegerField()
    dropoff_docks = models.IntegerField()
    latitude = models.DecimalField(max_digits=22, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=6, blank=True, null=True)


    def save(self,*args,**kwargs):
        geolocator = Nominatim(user_agent='main')
        location = geolocator.geocode(self.postcode)
        self.latitude = location.latitude
        self.longitude = location.longitude
        super(DockStation,self).save(*args,**kwargs)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('main:bikeavailibility',args=[self.id,])

class Booking(models.Model):
    booking_postcode = models.CharField(max_length=20)
    booking_from=models.TextField()
    booking_to=models.TextField(null=True,blank=True)
    has_pass = models.BooleanField(default=False)

    booking_time = models.TimeField()
    email =  models.EmailField()
    user= models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    status = models.BooleanField(default=False)
    bicycle_drop_status =  models.BooleanField(default=False)
    booking_date = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.user.username

class StripeCustomer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255,blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255,blank=True, null=True)
    stripeSubscriptionId = models.CharField(max_length=255,blank=True, null=True)
    cancel_at_day_end = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class StripePasses(models.Model):
    pass_name = models.CharField(max_length=255,blank=True, null=True)
    pass_stripeID = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return self.pass_name


class userhasbike(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    has_bike = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class user_booking_history(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    starting_point = models.CharField(max_length=255,blank=True, null=True)
    pass_type =  models.CharField(max_length=255,blank=True, null=True)
    amount_charged =  models.CharField(max_length=255,blank=True, null=True)
    time_of_purchase = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

