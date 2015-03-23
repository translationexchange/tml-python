from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tml_django_demo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'tml_django_demo.views.home'),
    url(r'^translate$', 'tml_django_demo.views.translate'),
)
