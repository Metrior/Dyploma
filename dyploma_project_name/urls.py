from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^q/', include('quiz.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('loginsys.urls')),
)
