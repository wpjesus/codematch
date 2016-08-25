from django import forms
from django.forms import ModelForm
from ietf.codestand.requests.models import CodeRequest
from ietf.codestand.matches.models import ProjectTag
from ietf.person.fields import SearchablePersonField
from ietf.doc.fields import SearchableDocAliasField


class DocNameForm(forms.Form):
    # doc = forms.CharField(label="Document", max_length=128, required=True)
    doc = SearchableDocAliasField(label="I-D name/RFC number", required=True, doc_type="draft")


class MentorForm(forms.Form):    
    mentor = SearchablePersonField(label="Must be present", required=False)
        

class TagForm(ModelForm):
    class Meta:
        model = ProjectTag
        fields = ["name"]


class CodeRequestForm(ModelForm):
    class Meta:
        model = CodeRequest
        fields = ["mentor", "estimated_lof", "additional_information"]
