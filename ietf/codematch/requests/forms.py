from django import forms
from django.forms import ModelForm, CharField

from ietf.codematch.requests.models import CodeRequest

class CodeRequestForm(ModelForm):
    class Meta:
        model = CodeRequest
        fields = [ "estimated_lof" , "additional_information"]