from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
context = {'template_name' : 'authenticate/index.html'}
context_reset = {'template_name' : 'authenticate/reset.html'}
urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'authenticate.views.custom_register', name='register'),
    url(r'index', 'authenticate.views.custom_register', name='register'),
    url(r'signin', 'authenticate.views.custom_login', name='signin'),
    url(r'register', 'authenticate.views.custom_register', name='register'),
    url(r'reset', 'authenticate.views.reset', name='reset'),
    url(r'logout', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'change_password', 'authenticate.views.change_password', name='passchange'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-\.]+)/(?P<token>[a-z0-9\-]+)$', 'authenticate.views.confirm_registration', name='confirm'),
)
