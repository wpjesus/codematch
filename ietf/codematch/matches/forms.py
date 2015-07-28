from django import forms
from django.forms import ModelForm, CharField

from django.utils.translation import ugettext_lazy as _

from ietf.codematch.matches.models import ProjectContainer, CodingProject

from ietf.doc.fields import SearchableDocAliasField
from ietf.doc.models import DocAlias

class SearchForm(forms.Form):
    title = forms.CharField(label="Title", max_length=255, required=False)
    protocol = forms.CharField(label="Protocol", required=False)
    description = forms.CharField(label="Description", max_length=255,required=False)
    doctitle = forms.CharField(label="Words in document title", max_length=128,required=False)
    coder = forms.CharField(label="First Name or Last Name", max_length=128,required=False)

class DocNameForm(forms.Form):
    name = forms.CharField(label="Name", max_length=128,required=True)

class ProjectContainerForm(ModelForm):
    class Meta:
        model = ProjectContainer
        fields = [ "title", "protocol", "description" ]

class CodingProjectForm(ModelForm):
    class Meta:
        model = CodingProject
        fields = [ "coder", "title" , "additional_information" , "link_to_implementation" ]
        