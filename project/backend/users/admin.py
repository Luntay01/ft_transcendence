from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User

# Register your models here.
class UserCreationForm(UserCreationForm):
	class Meta:
		model = User
		fields = '__all__'

class UserChangeFrom(UserChangeForm):
	class Meta:
		model = User
		fields = '__all__'

class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ("email", "username", "is_staff", "is_active",)
    list_filter = ("email", "username", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password", "username")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "username", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)

admin.site.register(User, UserAdmin)