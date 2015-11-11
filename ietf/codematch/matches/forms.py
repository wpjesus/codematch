from django import forms
from django.forms import ModelForm, CharField
from ietf.codematch.matches.models import ProjectContainer, CodingProject, Implementation, ProjectContact


class SearchForm(forms.Form):
    search = forms.CharField(label="Search", max_length=255, required=False)


class LinkImplementationForm(ModelForm):
    class Meta:
        model = Implementation
        fields = ["link"]


class ContactForm(ModelForm):
    class Meta:
        model = ProjectContact
        fields = ["contact", "type"]


class ProjectContainerForm(ModelForm):
    class Meta:
        model = ProjectContainer
        fields = ["title", "protocol", "description"]


class CodingProjectForm(ModelForm):
    class Meta:
        model = CodingProject
        fields = ["title", "additional_information"]
