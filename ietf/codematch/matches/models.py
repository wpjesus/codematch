from django.db import models

import debug
import datetime

from ietf.group.models import Group
from ietf.person.models import Person
from ietf.doc.models import DocAlias

from ietf.codematch.requests.models import CodeRequest

class CodingProject (models.Model):
    """ an element in ProjectContainer can have several Coding Projects"""
    """  implementing the proposal in different ways, or in different """
    """ repositories or by different groups or persons """   

    # This is the name that the student choose for his coding project
    title                  = models.CharField(max_length=80)
    # URL to github or other repository:
    link_to_implementation = models.URLField(blank=True)
    # Any other text that the coder would like to include as a description
    additional_information = models.CharField(max_length=255)
    
    # The coder must have a user account in datatracker (as a person)
    coder                  = models.ForeignKey(Person, null=True, blank=True)
    
    # When the coding project was added
    creation_date          = models.DateTimeField(auto_now_add=True)
    
    # TODO: this field is integer?
    reputation             = models.IntegerField(null=True, blank=True)
    
     # Each Project belongs to an entry in Project Container
    #project_container      = models.ForeignKey(ProjectContainer, blank=True, null=True)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.title
    
class ProjectContainer (models.Model):
    """ The ProjectContainer associates the Documents to the projects  """

    title                  = models.CharField(max_length=80)
    creation_date          = models.DateTimeField(auto_now_add=True)

    # Protocol that was implemented (if any):
    #(Note that this is a free text field )
    protocol               = models.CharField(max_length=255)
    description            = models.CharField(max_length=255)
    
    # Some elements will not have a CodeRequest
    code_request           = models.ForeignKey(CodeRequest, blank=True, null=True)
    docs                   = models.ManyToManyField(DocAlias)
    
    codings                = models.ManyToManyField(CodingProject)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.title
