from django.db import models

import debug
import datetime

from ietf.group.models import Group
from ietf.person.models import Person
from ietf.doc.models import DocAlias

class CodeRequest (models.Model):
    """ A CodeRequest is additional information to a Project Container"""
    """ Some elements in the project Container do not have a CodeRequest"""
    """ because they're Past projects or may haven't been formaly """
    """ requested by an author """

    #Estimated Level of Effort
    Estimated_LoF          = models.CharField(max_length=80)
    # The author can include additional text to describe his request
    Additional_information = models.CharField(max_length=255)
    user                   = models.ForeignKey(Person)
    time                   = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.Additional_information


class ProjectContainer (models.Model):
    """ The ProjectContainer associates the Documents to the projects  """

    Title                  = models.CharField(max_length=80)
    Creation_date          = models.DateTimeField(auto_now_add=True)

    # Protocol that was implemented (if any):
    #(Note that this is a free text field )
    Protocol               = models.CharField(max_length=255)
    Description            = models.CharField(max_length=255)

    Person = models.ForeignKey(Person, blank=True, null=True)
    # Some elements will not have a CodeRequest
    CodeRequest            = models.ForeignKey(CodeRequest, blank=True, null=True)
    docs = models.ManyToManyField(DocAlias)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.Title

class CodingProject (models.Model):
    """ an element in ProjectContainer can have several Coding Projects"""
    """  implementing the proposal in different ways, or in different """
    """ repositories or by different groups or persons """   

    # This is the name that the student choose for his coding project
    Title = models.CharField(max_length=80)
    # URL to github or other repository:
    Link_to_Implementation = models.URLField(blank=True)

    # Any other text that the coder would like to include as a description
    Additional_Information = models.CharField(max_length=255)

    # The coder must have a user account in datatracker (as a person)
    User = models.ForeignKey(Person, blank=True, null=True)
    # When the coding project was added
    time                   = models.DateTimeField(auto_now_add=True)

     # Each Project belongs to an entry in Project Container
    ProjectContainer = models.ForeignKey(ProjectContainer, blank=True, null=True)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.Title
