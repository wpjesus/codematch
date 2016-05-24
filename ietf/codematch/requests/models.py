from django.db import models


class CodeRequest(models.Model):
    """ A CodeRequest is additional information to a Project Container"""
    """ Some elements in the project Container do not have a CodeRequest"""
    """ because they're Past projects or may haven't been formaly """
    """ requested by an author """

    # mentor = models.ForeignKey(Person, null=True, blank=True)
    mentor = models.IntegerField(blank=True, null=True)

    # Estimated Level of Effort
    estimated_lof = models.FloatField(null=True, blank=True)

    # The author can include additional text to describe his request
    additional_information = models.CharField(max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.additional_information
