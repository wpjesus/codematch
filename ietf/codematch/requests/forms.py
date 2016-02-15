from django import forms
from django.forms import ModelForm
from ietf.codematch.requests.models import CodeRequest
from ietf.codematch.matches.models import ProjectTag
from ietf.person.models import Person
from dal import autocomplete


class DocNameForm(forms.Form):
    doc = forms.CharField(label="Document", max_length=128, required=True)


class MentorForm(forms.Form):    
    # mentor = forms.ModelChoiceField(Person.objects.all(), widget=autocomplete.ModelSelect2(url='personcomplete'))
    mentor = forms.ModelChoiceField(Person.objects.all())


class TagForm(ModelForm):
    class Meta:
        model = ProjectTag
        fields = ["name"]


class CodeRequestForm(ModelForm):
    class Meta:
        model = CodeRequest
        fields = ["mentor", "estimated_lof", "additional_information"]
