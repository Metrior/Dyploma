from django.shortcuts import render, redirect, render_to_response
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt


from forms import RegistrationForm

@csrf_exempt

def login(request):
    args={}
    if request.POST:
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/q/test/')
        else:
            args['login_error']="User not found"
            return render_to_response('login.html', args)
    else:
        return render_to_response('login.html', args)


def logout(request):
    auth.logout(request)
    return redirect('/q/test/')

@csrf_exempt

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            newuser = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            auth.login(request, newuser)
            return redirect('/q/test/')
    else:
        form = RegistrationForm()

    return render(request, 'registration_form.html', {'form': form})























# from django.views.genetic import FormView
# from django.auth.forms import UserCreationForm
# from django.core.context_processor import csrf

# class Register(FormView):
#     form_class=RegistrationForm
#     template_name='registration_form.html'
#     def register(request):
#         args={}
#         args['form']=UserCreationForm()
#         if request.POST:
#             newuser_form=UserCreationForm(request.POST)
#             if newuser_form.is_valid():
#                 newuser_form.save()
#                 newuser=auth.authenticate(username=newuser_form.cleaned_data['username'], password=newuser_form.cleaned_data['password1'])
#                 # email = forms.EmailField(label=("E-mail"))
#                 auth.login(request, newuser)
#                 return redirect('/q/')
#             else:
#                 args['forms']=newuser_form
#         return render_to_response('registration_form.html', args)


# from django.shortcuts import redirect
# from django.views.generic.base import TemplateView
# from django.views.generic.edit import FormView
# from django.conf import settings
# from django.utils.decorators import method_decorator
# from django.utils.module_loading import import_string
# from django.views.decorators.debug import sensitive_post_parameters
#
#
#
# REGISTRATION_FORM_PATH = getattr(settings, 'REGISTRATION_FORM',
#                                  'registration.forms.RegistrationForm')
# REGISTRATION_FORM = import_string(REGISTRATION_FORM_PATH)
# ACCOUNT_AUTHENTICATED_REGISTRATION_REDIRECTS = getattr(settings, 'ACCOUNT_AUTHENTICATED_REGISTRATION_REDIRECTS', True)
#
#
# class RegistrationView(FormView):
#     """
#     Base class for user registration views.
#     """
#     disallowed_url = 'registration_disallowed'
#     form_class = REGISTRATION_FORM
#     http_method_names = ['get', 'post', 'head', 'options', 'trace']
#     success_url = None
#     template_name = 'templates/registration_form.html'
#
#     @method_decorator(sensitive_post_parameters('password1', 'password2'))
#     def dispatch(self, request, *args, **kwargs):
#         """
#         Check that user signup is allowed and if user is logged in before even bothering to
#         dispatch or do other processing.
#         """
#         if ACCOUNT_AUTHENTICATED_REGISTRATION_REDIRECTS:
#             if self.request.user.is_authenticated():
#                 if settings.LOGIN_REDIRECT_URL is not None:
#                     return redirect(settings.LOGIN_REDIRECT_URL)
#                 else:
#                     raise Exception("You must set a URL with LOGIN_REDIRECT_URL in settings.py or set ACCOUNT_AUTHENTICATED_REGISTRATION_REDIRECTS=False")
#
#         if self.request.user.is_authenticated():
#             return redirect(settings.LOGIN_REDIRECT_URL)
#         if not self.registration_allowed():
#             return redirect(self.disallowed_url)
#         return super(RegistrationView, self).dispatch(request, *args, **kwargs)
#
#     def form_valid(self, form):
#         new_user = self.register(form)
#         success_url = self.get_success_url(new_user)
#
#         # success_url may be a simple string, or a tuple providing the
#         # full argument set for redirect(). Attempting to unpack it
#         # tells us which one it is.
#         try:
#             to, args, kwargs = success_url
#         except ValueError:
#             return redirect(success_url)
#         else:
#             return redirect(to, *args, **kwargs)
#
#     def registration_allowed(self):
#         """
#         Override this to enable/disable user registration, either
#         globally or on a per-request basis.
#         """
#         return True
#
#     def register(self, form):
#         """
#         Implement user-registration logic here.
#         """
#         raise NotImplementedError
#
#     def get_success_url(self, user=None):
#         """
#         Use the new user when constructing success_url.
#         """
#         return super(RegistrationView, self).get_success_url()
