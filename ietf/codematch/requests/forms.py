from django import forms
from django.forms import ModelForm
from ietf.codematch.requests.models import CodeRequest
from ietf.codematch.matches.models import ProjectTag
from ietf.person.models import Person


class DocNameForm(forms.Form):
    doc = forms.CharField(label="Document", max_length=128, required=True)


class MentorForm(forms.Form):    
    mentor = forms.ModelChoiceField(Person.objects.using('datatracker').all())

    def __init__(self,*args,**kwargs):
        super(MentorForm, self).__init__(*args,**kwargs)
        self.fields['mentor'].queryset = Person.objects.using('datatracker').all()

class TagForm(ModelForm):
    class Meta:
        model = ProjectTag
        fields = ["name"]


class CodeRequestForm(ModelForm):
    class Meta:
        model = CodeRequest
        fields = ["mentor", "estimated_lof", "additional_information"]
