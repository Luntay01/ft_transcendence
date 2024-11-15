from django.contrib import admin
from .models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms

# Register your models here.
class UserForm(forms.ModelForm):
	password = forms.CharField(
		label=("Password"),
		widget=forms.PasswordInput,
	)

	class Meta:
		model = User
		fields = ['username', 'password', 'email']

class UserAdmin(admin.ModelAdmin):
	list_display = ['username', 'password', 'email']
	form = UserForm

admin.site.register(User, UserAdmin)