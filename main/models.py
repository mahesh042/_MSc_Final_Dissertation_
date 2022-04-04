from django.db import models
from django.contrib.auth.models import User

class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    time_st = models.DateTimeField(auto_now=True)
    otp = models.PositiveSmallIntegerField()


class DockStation(models.Model): 
   name = models.CharField(max_length=255)
   address = models.CharField(max_length=200) 
   postcode = models.CharField(max_length=10) 
   latitude = models.FloatField() 
   longitude = models.FloatField() 
