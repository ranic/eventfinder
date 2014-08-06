from django import forms
from django.contrib.auth import authenticate

#from events.models import GeoLocUser
from django.contrib.auth.models import User

class EmailInput(forms.widgets.Input):
	input_type='email'

""" Mostly taken from the DjangoForms example from class """
class RegistrationForm(forms.Form):
	name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Name'}))
	username = forms.CharField(max_length = 40, widget=EmailInput(attrs={'placeholder': 'Email'}), label='Email')
	password1 = forms.CharField(max_length = 20, 
	                            label='Password', 
	                            widget = forms.PasswordInput(attrs={'placeholder': 'Password'}))
	password2 = forms.CharField(max_length = 20, 
	                            label='Confirm password',  
	                            widget = forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))


	# Customizes form validation for properties that apply to more
	# than one field.  Overrides the forms.Form.clean function.
	def clean(self):
	    # Calls our parent (forms.Form) .clean function, gets a dictionary
	    # of cleaned data as a result
	    cleaned_data = super(RegistrationForm, self).clean()
	    username = cleaned_data.get('username')
	    if username and User.objects.filter(username__exact=username):
	        raise forms.ValidationError("Email is already taken.")
	    # Confirms that the two password fields match
	    password1 = cleaned_data.get('password1')
	    password2 = cleaned_data.get('password2')
	    if password1 and password2 and password1 != password2:
	        raise forms.ValidationError("Passwords did not match.")

	    # We must return the cleaned data we got from our parent.
	    return cleaned_data


class LoginForm(forms.Form):
	username = forms.CharField(max_length = 40, label='Email', widget=EmailInput(attrs={'placeholder': 'Email'}))
	password1 = forms.CharField(max_length = 20, 
	                            label='Password', 
	                            widget = forms.PasswordInput(attrs={'placeholder': 'Password'}))


	def clean(self):
	    # Calls our parent (forms.Form) .clean function, gets a dictionary
	    # of cleaned data as a result
	    cleaned_data = super(LoginForm, self).clean()

	    # Confirms that the two password fields match
	    password1 = cleaned_data.get('password1')
	    username = cleaned_data.get('username')
	    if username and not User.objects.filter(username__exact=username):
	        raise forms.ValidationError("Username does not exist.")
	    if username and password1 and not authenticate(username=username, password=password1):
	        raise forms.ValidationError("Invalid password for user %s." % username)

	    # We must return the cleaned data we got from our parent.
	    return cleaned_data

class PasswordChangeForm(forms.Form):
	username = forms.CharField(max_length = 40, label='Email', widget=EmailInput(attrs={'placeholder': 'Email'}))
	curPassword = forms.CharField(max_length = 20, 
	                            label='Current Password', 
	                            widget = forms.PasswordInput(attrs={'placeholder': 'Password'}))
	password = forms.CharField(max_length = 20, 
	                            label='New Password', 
	                            widget = forms.PasswordInput(attrs={'placeholder': 'New Password'}))
	confirmPass = forms.CharField(max_length = 20, 
	                            label='Confirm New Password', 
	                            widget = forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}))



	def clean(self):
		cleaned_data = super(PasswordChangeForm, self).clean()
		username = cleaned_data.get('username')
		curPassword = cleaned_data.get('curPassword')
		password = cleaned_data.get('password')
		confirmPass = cleaned_data.get('confirmPass')

		if username and not User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username does not exist.")
		if username and curPassword and not authenticate(username=username, password=curPassword):
			raise forms.ValidationError("Invalid password for user %s." % username)
		if password and confirmPass and password != confirmPass:
			raise forms.ValidationError("Passwords did not match.")

		return cleaned_data
