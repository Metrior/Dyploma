from django.conf.urls import patterns, include, url

from django.contrib import admin
from loginsys.views import login, logout, register
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^login/$', login,
        # view=Login.as_view(),
        # name='user_login'
        ),
    url(r'^logout/$', logout
        # view=Logout.as_view(),
        # name='user_logout'
        ),
    url(r'^register/$', register
        # view=Register.as_view(),
        # name='user_register'
        ),
)













# import warnings
#
# warnings.warn("include('registration.urls') is deprecated; use include('registration.backends.default.urls') instead.",
#               DeprecationWarning)
#
# from django.conf.urls import include
# from django.conf.urls import url
# from django.conf import settings
# from django.views.generic.base import TemplateView
#
#
# from .views import RegistrationView
#
#
#
# urlpatterns = [
#     url(r'^activate/complete/$',
#         TemplateView.as_view(template_name='registration/activation_complete.html'),
#         name='registration_activation_complete'),
#
#     # Activation keys get matched by \w+ instead of the more specific
#     # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
#     # that way it can return a sensible "invalid key" message instead of a
#     # confusing 404.
#
#     url(r'^register/complete/$',
#         TemplateView.as_view(template_name='registration/registration_complete.html'),
#         name='registration_complete'),
#     url(r'^register/closed/$',
#         TemplateView.as_view(template_name='registration/registration_closed.html'),
#         name='registration_disallowed'),
# ]
#
# if getattr(settings, 'INCLUDE_REGISTER_URL', True):
#     urlpatterns += [
#         url(r'^register/$',
#             RegistrationView.as_view(),
#             name='registration_register'),
#     ]
#
# if getattr(settings, 'INCLUDE_AUTH_URLS', True):
#     urlpatterns += [
#         url(r'', include('registration.auth_urls')),
#     ]
