# from django.conf.urls import include
# from django.conf.urls import url
# from django.conf import settings
# from django.views.generic.base import TemplateView
#
# from .views import RegistrationView
#
#
# urlpatterns = [
#     url(r'^register/closed/$',
#         TemplateView.as_view(template_name='registration/registration_closed.html'),
#         name='registration_disallowed'),
# ]
#
# if getattr(settings, 'INCLUDE_REGISTER_URL', True):
#     urlpatterns += [
#         url(r'^register/$',
#             RegistrationView.as_view(
#                 success_url=getattr(settings, 'SIMPLE_BACKEND_REDIRECT_URL', '/'),
#             ),
#             name='registration_register'),
#     ]
#
# if getattr(settings, 'INCLUDE_AUTH_URLS', True):
#     urlpatterns += [
#         url(r'', include('registration.auth_urls')),
#     ]