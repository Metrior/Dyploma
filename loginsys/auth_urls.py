# import django
#
# from django.conf.urls import url
# from django.core.urlresolvers import reverse_lazy
# from django.contrib.auth import views as auth_views
#
#
# if django.VERSION >= (1, 11):
#     urlpatterns = [
#         url(r'^login/$',
#             auth_views.LoginView.as_view(
#                 template_name='rtemplates/login.html'),
#             name='auth_login'),
#         url(r'^logout/$',
#             auth_views.LogoutView.as_view(
#                 template_name='templates/logout.html'),
#             name='auth_logout'),
#     ]
# else:
#     urlpatterns = [
#         url(r'^login/$',
#             auth_views.login,
#             {'template_name': 'templates/login.html'},
#             name='auth_login'),
#         url(r'^logout/$',
#             auth_views.logout,
#             {'template_name': 'templates/logout.html'},
#             name='auth_logout'),
#     ]