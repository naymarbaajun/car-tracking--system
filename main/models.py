from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    user_type_data = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)

class AdminHOD(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Cars(models.Model):
    id = models.AutoField(primary_key=True)
    car_name = models.CharField(max_length=255)
    car_color = models.CharField(max_length=255)
    car_model = models.CharField(max_length=255)
    year = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Owners(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=12)
    address = models.TextField()
    car = models.ForeignKey(Cars, on_delete=models.DO_NOTHING, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)  # Set default value here
    timestamp = models.DateTimeField(auto_now_add=True)
    car = models.ForeignKey(Cars, on_delete=models.CASCADE, default=1)