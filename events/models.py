from django.db import models
from django.db.models.signals import post_delete
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import os
from django.db import transaction
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode

SHORT = 50
LONG = 300

class RenameFilesModel(models.Model):
    """ Citation: https://djangosnippets.org/snippets/1129/ """
    RENAME_FILES = {}
    
    class Meta:
        abstract = True
    
    def save(self, force_insert=False, force_update=False):
        rename_files = getattr(self, 'RENAME_FILES', None)
        if rename_files:
            super(RenameFilesModel, self).save(force_insert, force_update)
            force_insert, force_update = False, True
            
            for field_name, options in rename_files.iteritems():
                field = getattr(self, field_name)
                file_name = force_unicode(field)
                name, ext = os.path.splitext(file_name)
                keep_ext = options.get('keep_ext', True)
                final_dest = options['dest']
                if callable(final_dest):
                    final_name = final_dest(self, file_name)
                else:
                    final_name = os.path.join(final_dest, '%s' % (self.pk,))
                    if keep_ext:
                        final_name += ext
                    setattr(self, 'filename', "%s.html" % self.pk)
                if file_name != final_name:
                    field.storage.delete(final_name)
                    field.storage.save(final_name, field)
                    field.storage.delete(file_name)
                    setattr(self, field_name, final_name)
        
        super(RenameFilesModel, self).save(force_insert, force_update)

class GeoLocUser(models.Model):
    """ Application user. Hosts and attends events. """

    user = models.OneToOneField(User)
    picture = models.ImageField(upload_to="profilepic",blank="True")

class Location(models.Model):
    """ Wraps the Google Maps API location. Stores location of events. """

    longitude = models.DecimalField(decimal_places=5, max_digits=20)
    latitude = models.DecimalField(decimal_places=5, max_digits=20)


class Plugin(RenameFilesModel):
    """ Plugin that uses data from the database to customize the rendering of event pages """
    name = models.CharField(max_length=SHORT)
    template = models.FileField(upload_to='plugins/')
    filename = models.CharField(max_length=LONG)

    RENAME_FILES = {
        'template': {'dest': 'plugins/', 'keep_ext': True}
    }

    def __unicode__(self):
        return self.name

# Citation: http://stackoverflow.com/questions/16041232/django-delete-filefield
# Deletes files associated with invalid plugins when they are deleted
@receiver(post_delete, sender=Plugin)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Plugin` object is deleted.
    """
    if instance.template:
        if os.path.isfile(instance.template.path):
            os.remove(instance.template.path)

@receiver(models.signals.pre_save, sender=Plugin)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Plugin` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = (Plugin.objects.get(pk=instance.pk)).template
    except Plugin.DoesNotExist:
        return False

    new_file = instance.template
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

#############################
### Event related classes ###
#############################
class Event(models.Model):
    """ A real-world event. Has a host, attensdees, tags, testimonials, and pictures. """

    name = models.CharField(max_length=SHORT)
    description = models.CharField(max_length=LONG)
    
    # Only one user can host an event
    host = models.ForeignKey(GeoLocUser, related_name='hosted_events')
    guests = models.ManyToManyField(GeoLocUser, related_name='events')
    
    # Duration of the event
    start = models.DateTimeField()
    end = models.DateTimeField()

    # Each event has exactly one location. A location can have many events
    location = models.ForeignKey(Location, related_name='events', blank=True)

    # Photo associated with eventw
    picture = models.ImageField(upload_to="eventpic",blank="True")

    #When an event ends, mark as inactive
    active = models.BooleanField(default=True)
    plugin = models.ForeignKey(Plugin, related_name='events')

    def get_plugin(self):
        return self.plugin

    def set_plugin(self, p):
        self.plugin = p
        self.save()
        return

    #@staticmethod
    def is_active(self):
        """ Return whether this event is currently happening """
        curTime = timezone.now()
        afterStart = (curTime - self.start) > timedelta(seconds=0)
        beforeEnd = (self.end - curTime) > timedelta(seconds=0)
        return (afterStart and beforeEnd)

    def is_upcoming(self):
        curTime = timezone.now()
        beforeEnd = (self.end - curTime) > timedelta(seconds=0)
        return beforeEnd

@transaction.commit_on_success
def create_plugin(name, template, filename):
    """ Doesn't allow users to overwrite plugins that have the same name """
    try:
        p = Plugin.objects.get(name__exact=name)
    except:
        p = Plugin(name=name, template=template, filename=filename)
        p.save()
    finally:
        return p

class Tag(models.Model):
    """ Tag is an identifier of an event. Can search to find similar events """

    text = models.CharField(max_length=SHORT)
    events = models.ManyToManyField(Event, related_name='tags')

class Testimonial(models.Model):
    """ Testimonial is text about an event posted by a user """
    
    text = models.CharField(max_length=LONG)
    user = models.ForeignKey(GeoLocUser, related_name='testimonials')
    event = models.ForeignKey(Event, related_name='testimonials')
    image = models.ImageField(upload_to='eventpics/', blank=True)


