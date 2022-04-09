from asyncio.windows_events import NULL
from django.db import models
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim

class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    time_st = models.DateTimeField(auto_now=True)
    otp = models.PositiveSmallIntegerField()


class DockStation(models.Model): 
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=200) 
    postcode = models.CharField(max_length=10) 
    description = models.TextField(blank=True)
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
