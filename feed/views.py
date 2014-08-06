from django.shortcuts import render, redirect, get_object_or_404

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from events.models import Location, Event, GeoLocUser, Tag, Testimonial
from django.db import transaction
from math import sin, cos, sqrt, atan2, radians, asin
from operator import itemgetter

EARTH_RADIUS = 3959 # miles
FEET_IN_MILE = 5280

@transaction.commit_on_success
@login_required
def updateFeed(request):
    context = {}
    # Assume loc = user's current location, radius = request's radius
    lng = request.GET['lng']
    lat = request.GET['lat']
    radius = float(request.GET['radius'])
    loc = (float(lat), float(lng))

    #Each event is mapped to its distance from the user (who is at loc)
    events = [(e, distance(loc, e.location.latitude, e.location.longitude)) \
               for e in Event.objects.all() if e.is_upcoming()]
    eventsInRadius = filter(lambda (_, d): (d < radius), events)
    eventsInRadius.sort(key=itemgetter(1))
    eventsInRadius = map(stringDist, eventsInRadius)

    #(Event, distance) list
    context['feed'] =  eventsInRadius

    return render(request, 'feed/eventInfo.xml', context, content_type='application/xml');

@transaction.commit_on_success
@login_required
def displayFeed(request):
    context = {}
    context['user'] = request.user
    return render(request, 'feed/index.html', context)

#Distance as a string. If less than 0.2 miles, return __ ft.
def stringDist((e, d)):
    if (d < 0.1):
        return (e, "\t%d.0 feet away  " % (int(d*FEET_IN_MILE)))
    else:
        return (e, "%.2f miles away" % d)

#Code implementing haversine formula to calculate distance between two latitude and longitude points
@transaction.commit_on_success
def distance((x1,y1), x2, y2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [y1, x1, y2, x2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    miles = EARTH_RADIUS * c
    return miles

@transaction.commit_on_success
@login_required
def search(request):
    context = {}
    context['user'] = request.user
    if request.method == "GET":
        return render(request, 'feed/search.html', context)

    context['query'] = request.POST['query']
    tags = set(context['query'].lower().split(' '))
    events = Event.objects.all()
    context['events'] = [e for e in events if (e.is_upcoming() and isMatch(e, tags))]

    return render(request, 'feed/search.html', context)

@transaction.commit_on_success
@login_required
def api(request):
    context = {}
    context['user'] = request.user
    context['error'] = ""
    return render(request, 'feed/plugin_api.html', context)

@transaction.commit_on_success
@login_required
def my_current_events(request):
    context = {}
    context['user'] = request.user
    context['current_events'] = reversed([e for e in request.user.geolocuser.events.order_by('-start') if e.is_upcoming()])

    return render(request, 'feed/currentevents.html', context)

@transaction.commit_on_success
def isMatch(e, t):
    for tag in e.tags.all():
        if tag.text.lower() in t:
            return True
    for n in e.name.lower().split(' '):
        if n in t:
            return True
    for d in e.description.lower().split(' '):
        if d in t:
            return True
    return False
