from django.db import models
from django.contrib.auth.models import User 
import random
# Create your models here.
class UserProfile(models.Model):

    USER_TYPES = [
        ('Public', 'Public'),
        ('Owner','Owner'),
        ('Admin', 'Admin'),
    ]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    profilePicture = models.ImageField(blank=True, null=True)
    DOB = models.DateField()
    address = models.TextField()
    contact_No = models.IntegerField()
    gender=models.CharField(max_length=50,null=True,blank=True)
    userType = models.CharField(max_length=10, choices=USER_TYPES, default='Public')
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username

class OTP(models.Model):
    def Get_OTP():
        return random.randint(100000, 999999)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.IntegerField(default=Get_OTP)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username