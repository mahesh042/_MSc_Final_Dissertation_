from zoneinfo import available_timezones
from django.db import models
from django.contrib.auth.models import User

class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    time_st = models.DateTimeField(auto_now=True)
    otp = models.PositiveSmallIntegerField()


class DockStations(models.Model):
    station_id = models.IntegerField()
    post_code = models.TextField()
    docks = models.IntegerField()
    pickup_docks = models.IntegerField()
    dropoff_docks = models.IntegerField()
    class Meta:
        unique_together = ['post_code']
