from django.conf.urls import patterns, include, url
from events.models import Plugin

# Generates the routes for the Controller.
# Typical use is a regular expression for a URL pattern, and then the
# action to call to process requests for that URL pattern.
urlpatterns = patterns('',
    url(r'^$', 'feed.views.displayFeed', name='displayFeed'),
    url(r'^eventpage(?P<id>\d+)$', 'events.views.viewEvent', name='eventpage'),
    url(r'^create', 'events.views.createEvent', name='create'),
    url(r'^join(?P<id>\d+)$', 'events.views.joinEvent', name='joinEvent'),
    url(r'^leave(?P<id>\d+)$', 'events.views.leaveEvent', name='leaveEvent'),
    url(r'^testimonial(?P<id>\d+)$', 'events.views.addTestimonial', name='testimonial'),
    url(r'^testimonial_photo(?P<id>\d+)$', 'events.views.get_testimonial_photo', name='testimonial_photo'),
    url(r'^upload_plugin', 'events.views.upload_plugin', name='upload_plugin'),
    url(r'^edit(?P<id>\d+)$', 'events.views.edit_event', name='edit'),
    url(r'^event_photo(?P<id>\d+)$', 'events.views.get_event_photo', name='event_photo'),
)
