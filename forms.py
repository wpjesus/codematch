from django import forms
from django.forms import ModelForm, CharField
from ietf.codematch.models import CodeRequest, ProjectContainer, CodingProject
from ietf.doc.fields import SearchableDocAliasField
from ietf.doc.models import DocAlias

class SearchForm(forms.Form):
    title = forms.CharField(label="Title", max_length=255, required=False)
    protocol = forms.CharField(label="Protocol", required=False)
    description = forms.CharField(label="Description", max_length=255,required=False)
    doctitle = forms.CharField(label="Words in document title", max_length=128,required=False)
    person = forms.CharField(label="First Name or Last Name", max_length=128,required=False)

class DocNameForm(forms.Form):
    name = forms.CharField(label="name", max_length=128,required=True)

class ProjectContainerForm(ModelForm):
    class Meta:
        model = ProjectContainer
        fields = [ "Title" , "Protocol" , "Description"]

class CodingProjectForm(ModelForm):
    class Meta:
         model = CodingProject
         fields = [ "Title" , "Additional_Information" , "Link_to_Implementation" ]
