from django import forms
from django.forms import ModelForm, CharField

from ietf.codematch.requests.models import CodeRequest
from ietf.codematch.matches.models import ProjectTag

class DocNameForm(forms.Form):
    doc = forms.CharField(label="Name", max_length=128, required=True)
    
class TagForm(ModelForm):
    class Meta:
        model = ProjectTag
        fields = [ "name" ]

class CodeRequestForm(ModelForm):
    class Meta:
        model = CodeRequest
        fields = [ "mentor", "estimated_lof" , "additional_information" ]