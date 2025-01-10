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
    list_display = (
        "id", "email", "provider", "oauth_user_id", "username", "picture",
        "first_name", "last_name", "birth_day", "is_staff", "is_active",
        )
    list_filter = (
        "id", "email", "provider", "oauth_user_id", "username", "picture",
        "first_name", "last_name", "birth_day", "is_staff", "is_active"
        )
    fieldsets = (
        (None, {"fields": (
            "email", "provider", "oauth_user_id", "password", "username", "picture",
            "first_name", "last_name", "birth_day"
            )}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "provider", "oauth_user_id", "password1", "password2", "username",
                "first_name", "last_name", "birth_date", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("id", "email",)
    ordering = ("id",)

admin.site.register(User, UserAdmin)