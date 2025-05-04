from django.contrib import admin
from .models import UserProfile,OTP
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display=['id','user']
admin.site.register(UserProfile,UserAdmin)
admin.site.register(OTP)
