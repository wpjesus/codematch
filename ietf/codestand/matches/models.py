from django.db import models
from ietf.codestand import constants
from ietf.codestand.requests.models import CodeRequest


class Implementation(models.Model):
    """  """

    link = models.URLField(blank=True)

    def __unicode__(self):
        return self.link


class ProjectTag(models.Model):
    """ """

    name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name


class ProjectContact(models.Model):
    """ """

    contact = models.CharField(max_length=80)
    type = models.CharField(max_length=50, choices=constants.MAIL_TYPES)

    def __unicode__(self):
        return self.contact


class CodingProject(models.Model):
    """ an element in ProjectContainer can have several Coding Projects"""
    """  implementing the proposal in different ways, or in different """
    """ repositories or by different groups or persons """

    # This is the name that the student choose for his coding project
    title = models.CharField(max_length=200)
    # URL to github or other repository:
    # link_to_implementation = models.URLField(blank=True)
    links = models.ManyToManyField(Implementation, blank=True, null=True)
    # Any other text that the coder would like to include as a description
    additional_information = models.CharField(max_length=255)

    # The coder must have a user account in datatracker (as a person)
    #coder = models.ForeignKey(Person, null=True, blank=True)
    coder = models.IntegerField(null=True, blank=True)

    # When the coding project was added
    creation_date = models.DateTimeField(auto_now_add=True)

    # TODO: this field is integer?
    reputation = models.IntegerField(null=True, blank=True)

    tags = models.ManyToManyField(ProjectTag, blank=True, null=True)

    # Each Project belongs to an entry in Project Container
    # project_container      = models.ForeignKey(ProjectContainer, blank=True, null=True)

    def __unicode__(self):  # __unicode__ on Python 2
        return self.title

class ProjectContainer(models.Model):
    """ The ProjectContainer associates the Documents to the projects  """

    # owner = models.ForeignKey(Person, null=True, blank=True)
    owner = models.IntegerField(null=True, blank=True)

    title = models.CharField(max_length=80)
    creation_date = models.DateTimeField(auto_now_add=True)

    # Protocol that was implemented (if any):
    # (Note that this is a free text field )
    protocol = models.CharField(max_length=255)
    description = models.TextField()

    # Some elements will not have a CodeRequest
    code_request = models.ForeignKey(CodeRequest, blank=True, null=True)
    
    # docs = models.ManyToManyField(DocAlias)
    # TODO: Thinks about use the CommaSeparatedIntegerField
    docs = models.CharField(max_length=10000, blank=True, null=True)
    
    codings = models.ManyToManyField(CodingProject)

    tags = models.ManyToManyField(ProjectTag, blank=True, null=True)

    contacts = models.ManyToManyField(ProjectContact, blank=True, null=True)

    def __unicode__(self):  # __unicode__ on Python 2
        return self.title
