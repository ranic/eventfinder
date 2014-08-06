from django.conf.urls import patterns, include, url
from django.core.files import File
from events.models import create_plugin
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('', 
    url(r'^$', include('authenticate.urls')),
    url(r'^authenticate/', include('authenticate.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^feed/', include('feed.urls')),
)


# Create the default plugin before all others
default = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'media', 'plugins', '1.html')

with open(default) as f:
    create_plugin(name='default', template=File(f), filename='1.html')
