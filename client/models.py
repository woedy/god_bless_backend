import os
import random
from accounts import models

def get_file_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_file_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "client/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )

def get_default_profile_image():
    return "defaults/default_profile_image.png"




class Client(models.Model):
    full_name = models.CharField(max_length=1000, unique=False, blank=True, null=True)
    dob = models.CharField(max_length=100, blank=True, null=True)
    drivers_licence = models.CharField(max_length=100, blank=True, null=True)
    social_security = models.CharField(max_length=100, blank=True, null=True)
    passport_number = models.CharField(max_length=100, blank=True, null=True)
    mothers_median_name = models.CharField(max_length=500, blank=True, null=True)
    
    photo = models.ImageField(upload_to=upload_image_path, null=True, blank=True, default=get_default_profile_image)

    phone = models.CharField(max_length=255, null=True, blank=True)
    carrier = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)


    country = models.CharField(max_length=255, null=True, blank=True)

    
    created_at = models.DateTimeField(auto_now_add=True)




class Address(models.Model):
    line1 = models.CharField(max_length=1000, blank=True, null=True)
    line2 = models.CharField(max_length=1000, blank=True, null=True)
    line3 = models.CharField(max_length=1000, blank=True, null=True)
    line4 = models.CharField(max_length=1000, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)




class CreditCard(models.Model):
    number = models.CharField(max_length=100, blank=True, null=True)
    ccv = models.CharField(max_length=100, blank=True, null=True)
    expiry = models.CharField(max_length=100, blank=True, null=True)
    pin = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)





class BankInfo(models.Model):
    bank_name = models.CharField(max_length=1000, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    
    username = models.CharField(max_length=500, blank=True, null=True)
    email = models.CharField(max_length=500, blank=True, null=True)
    password = models.CharField(max_length=500, blank=True, null=True)
    pin = models.CharField(max_length=100, blank=True, null=True)
    set_code = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)



class Financial(models.Model):
    username = models.CharField(max_length=1000, blank=True, null=True)
    password = models.CharField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)





class SocialMeidia(models.Model):
    platform = models.CharField(max_length=1000, blank=True, null=True)
    email = models.CharField(max_length=500, blank=True, null=True)
    username = models.CharField(max_length=500, blank=True, null=True)
    password = models.CharField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
