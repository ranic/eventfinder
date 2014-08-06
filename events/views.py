from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from events.models import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from forms import TestimonialForm, PluginForm, EventForm
from mimetypes import guess_type
import json
from django.db import transaction
from datetime import *
from django.core.urlresolvers import reverse
import os
from django.http import Http404

EVENT_REQUIRED_FIELDS = ['name', 'start', 'end']
DEFAULT_PLUGIN = Plugin.objects.get(id=1)

@transaction.commit_on_success
@login_required
def createEvent(request):
	context = {}
	context['user'] = request.user
	context['plugins'] = Plugin.objects.all()
	context['errors'] = []
	if(request.is_ajax() and request.method=="POST"):
		loc = Location(longitude=request.POST['lng'], latitude=request.POST['lat'])
		loc.save()
		plugin = Plugin.objects.get(name__exact=request.POST['plugin'])
		correct_start = request.POST['start'].replace('T', ' ')
		correct_end = request.POST['end'].replace('T', ' ')
		event = Event(host=context['user'].geolocuser, location=loc, name=request.POST['name'], description=request.POST['description'], start=correct_start, end=correct_end, plugin=plugin)
		event.save()
		event.guests.add(request.user.geolocuser)
		for tag in request.POST['tags'].split():
			try:
				t = Tag.objects.get(text__exact=tag)
			except ObjectDoesNotExist:
				t = Tag(text=tag)
				t.save()
			t.events.add(event)
			t.save()
		event.save()
		request_data = {'redirect' : settings.LOGIN_REDIRECT_URL}
		return HttpResponse(json.dumps(request_data), content_type='application/json')
	return render(request, 'events/create.html', context)

@transaction.commit_on_success
def get_event_photo(request, id):
    event = get_object_or_404(Event, id=id)
    if not event.picture:
        raise Http404

    content_type = guess_type(event.picture.name)
    return HttpResponse(event.picture, mimetype=content_type)

@transaction.commit_on_success
@login_required
def joinEvent(request, id):
	context = {}
	context['user'] = request.user
	event = get_object_or_404(Event, id=id)
	event.guests.add(request.user.geolocuser)
	event.save()

	return redirect(request.META.get('HTTP_REFERER', settings.LOGIN_REDIRECT_URL))

@transaction.commit_on_success
@login_required
def leaveEvent(request, id):
	context = {}
	context['user'] = request.user
	event = get_object_or_404(Event, id=id)
	event.guests.remove(request.user.geolocuser)
	event.save()

	return redirect(request.META.get('HTTP_REFERER', settings.LOGIN_REDIRECT_URL))

@transaction.commit_on_success
@login_required
def viewEvent(request, id):
	context = {}
	context['user'] = request.user
	context['event'] = get_object_or_404(Event, id=id)
	context['event_is_active'] = context['event'].is_active()
	""" If leave is true, then the user will have the option to leave the event """
	context['leave'] = context['event'].guests.filter(user=request.user.geolocuser).exists()
	return render(request, context['event'].get_plugin().filename, context)

#Post a testimonial to an event of the id
@transaction.commit_on_success
@login_required
def addTestimonial(request, id):
	context = {}
	context['user'] = request.user
	context['event'] = get_object_or_404(Event, id=id)
	if request.method == "GET":
		return redirect(request.META['HTTP_REFERER'])
	else:
		form = TestimonialForm(request.POST, request.FILES)
		if form.is_valid():
			text = form.cleaned_data['text']
			image = form.cleaned_data['image']
			testimonial = Testimonial(text=text, image=image, user=request.user.geolocuser, event=context['event'])
			testimonial.save()
		return redirect(request.META['HTTP_REFERER'])


@transaction.commit_on_success
def get_testimonial_photo(request, id):
	testimonial = Testimonial.objects.get(id=id)

	if not testimonial.image:
		raise Http404

	content_type = guess_type(testimonial.image.name)
	return HttpResponse(testimonial.image, mimetype=content_type)

@transaction.commit_on_success
@login_required
def upload_plugin(request):
	context = {}
	context['user'] = request.user
	if request.method == "POST":
		form = PluginForm(request.POST, request.FILES)
		if form.is_valid():
			name = form.cleaned_data.get('name')
			template = form.cleaned_data.get('template')
			filename = template._name
			p = create_plugin(name=name, template=template, filename=filename)
			p.save()
			context['event'] = get_object_or_404(Event, id=1)
			try:
				validate_plugin(p)
				context['event'].set_plugin(p)
				context['dummy'] = True
				return render(request, p.filename, context)
			except Exception as e:
				context['error'] = e
				p.delete()
				context['event'].set_plugin(DEFAULT_PLUGIN)
				return render(request, 'feed/bad_plugin.html', context)
	return redirect(settings.LOGIN_REDIRECT_URL)

@transaction.commit_on_success
def validate_plugin(p):
	p.template.open('rb')
	template_text = p.template.read().split('\n')
	p.template.close()
	firstLine = template_text[0]
	stripped = "".join(firstLine.split())
	if stripped != "{%extends'events/base_event.html'%}":
		raise Exception("First line of file must be: {%% extends 'events/base_event.html' %%}. \
						\n It is currently %s" % firstLine)

	for i, line in enumerate(template_text):
		splitLine = "".join(line.split())
		if '<form' in splitLine:
			raise Exception("Line %d contains a form. Forms are not allowed in templates.\n Line: %s." \
								% (i, line))
		if '<script' in splitLine:
			raise Exception("Line %d contains a script. Forms are not allowed in templates. \nLine: %s." \
								% (i, line))
	return

@transaction.commit_on_success
@login_required
def edit_event(request, id):
	context = {}
	context['user'] = request.user
	context['event'] = get_object_or_404(Event, id=id)
	# Only the host of the event can edit (prevents url hacking)
	if context['user'].geolocuser != context['event'].host:
		raise Http404

	if request.method=="GET":
		context['form'] = EventForm(instance=context['event'])
		return render(request,'events/edit.html', context)

	form = EventForm(request.POST, request.FILES, instance=context['event'])
	if not form.is_valid():
		context['form'] = form
		return redirect(reverse('edit', args=[id]))
	form.save()
	return redirect(reverse('eventpage', args=[id]))
