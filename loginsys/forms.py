from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, render_to_response
from django.contrib import auth
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    """
    Form for registering a new user account.
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    """
    email = forms.EmailField(label=("E-mail"))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1','password2')













class Email(forms.EmailField):
    def clean(self, value):
        super(Email, self).clean(value)
        try:
            User.objects.get(email=value)
            raise forms.ValidationError("This email is already registered. Use the 'forgot password' link on the login page")
        except User.DoesNotExist:
            return value

@csrf_exempt
def register(request):
    args={}
    args['form']=UserCreationForm()
    if request.POST:
        newuser_form=UserCreationForm(request.POST)
        if newuser_form.is_valid():
            newuser_form.save()
            email = forms.EmailField()
            newuser=auth.authenticate(username=newuser_form.cleaned_data['username'], password=newuser_form.cleaned_data['password1'])
            auth.login(request, newuser)
            return redirect('/q/')
        else:
            args['forms']=newuser_form
    return render_to_response('registration_form.html', args)

# from __future__ import unicode_literals
#
#
# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.utils.translation import ugettext_lazy as _
#
# from .users import UserModel, UsernameField
#
# User = UserModel()
#
#
# class RegistrationFormUsernameLowercase(RegistrationForm):
#     """
#     A subclass of :class:`RegistrationForm` which enforces unique case insensitive
#     usernames, make all usernames to lower case.
#     """
#     def clean_username(self):
#         username = self.cleaned_data.get('username', '').lower()
#         if User.objects.filter(**{UsernameField(): username}).exists():
#             raise forms.ValidationError(_('A user with that username already exists.'))
#
#         return username
#
#
# class RegistrationFormTermsOfService(RegistrationForm):
#     """
#     Subclass of ``RegistrationForm`` which adds a required checkbox
#     for agreeing to a site's Terms of Service.
#     """
#     tos = forms.BooleanField(widget=forms.CheckboxInput,
#                              label=_('I have read and agree to the Terms of Service'),
#                              error_messages={'required': _("You must agree to the terms to register")})
#
#
# class RegistrationFormUniqueEmail(RegistrationForm):
#     """
#     Subclass of ``RegistrationForm`` which enforces uniqueness of
#     email addresses.
#     """
#     def clean_email(self):
#         """
#         Validate that the supplied email address is unique for the
#         site.
#         """
#         if User.objects.filter(email__iexact=self.cleaned_data['email']):
#             raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
#         return self.cleaned_data['email']