from django import forms
from events.models import Event, LONG

class TestimonialForm(forms.Form):
	text = forms.CharField(max_length=LONG, widget=forms.TextInput(attrs={'placeholder': 'Text'}))
	image = forms.FileField(required=False)

class PluginForm(forms.Form):
	name = forms.CharField(max_length=LONG, widget=forms.TextInput(attrs={'placeholder': 'Plugin Name'}))
	template = forms.FileField()

class EventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Event
        exclude = ()
        widgets = {'picture' : forms.FileInput()}
        fields = ('name', 'description', 'plugin', 'picture')
