from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'displayFeed', 'feed.views.displayFeed', name='displayFeed'),
    url(r'index', 'feed.views.displayFeed', name='index'),
    url(r'query', 'feed.views.search', name='search'),
	url(r'updateFeed', 'feed.views.updateFeed', name='updateFeed'),
	url(r'api', 'feed.views.api', name='apidocs'),
	url(r'currentevents', 'feed.views.my_current_events', name='currentevents')
)
