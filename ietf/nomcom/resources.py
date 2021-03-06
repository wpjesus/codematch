# Autogenerated by the mkresources management command 2014-11-13 23:53
from tastypie.resources import ModelResource
from tastypie.fields import ToOneField, ToManyField
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from ietf import api

from ietf.nomcom.models import *        # pyflakes:ignore


from ietf.group.resources import GroupResource
class NomComResource(ModelResource):
    group            = ToOneField(GroupResource, 'group')
    class Meta:
        queryset = NomCom.objects.all()
        serializer = api.Serializer()
        #resource_name = 'nomcom'
        filtering = { 
            "id": ALL,
            "public_key": ALL,
            "send_questionnaire": ALL,
            "reminder_interval": ALL,
            "initial_text": ALL,
            "group": ALL_WITH_RELATIONS,
        }
api.nomcom.register(NomComResource())

from ietf.dbtemplate.resources import DBTemplateResource
class PositionResource(ModelResource):
    nomcom           = ToOneField(NomComResource, 'nomcom')
    requirement      = ToOneField(DBTemplateResource, 'requirement', null=True)
    questionnaire    = ToOneField(DBTemplateResource, 'questionnaire', null=True)
    class Meta:
        queryset = Position.objects.all()
        serializer = api.Serializer()
        #resource_name = 'position'
        filtering = { 
            "id": ALL,
            "name": ALL,
            "is_open": ALL,
            "nomcom": ALL_WITH_RELATIONS,
            "requirement": ALL_WITH_RELATIONS,
            "questionnaire": ALL_WITH_RELATIONS,
        }
api.nomcom.register(PositionResource())

from ietf.person.resources import EmailResource
class NomineeResource(ModelResource):
    email            = ToOneField(EmailResource, 'email')
    duplicated       = ToOneField('ietf.nomcom.resources.NomineeResource', 'duplicated', null=True)
    nomcom           = ToOneField(NomComResource, 'nomcom')
    nominee_position = ToManyField(PositionResource, 'nominee_position', null=True)
    class Meta:
        queryset = Nominee.objects.all()
        serializer = api.Serializer()
        #resource_name = 'nominee'
        filtering = { 
            "id": ALL,
            "email": ALL_WITH_RELATIONS,
            "duplicated": ALL_WITH_RELATIONS,
            "nomcom": ALL_WITH_RELATIONS,
            "nominee_position": ALL_WITH_RELATIONS,
        }
api.nomcom.register(NomineeResource())

class ReminderDatesResource(ModelResource):
    nomcom           = ToOneField(NomComResource, 'nomcom')
    class Meta:
        queryset = ReminderDates.objects.all()
        serializer = api.Serializer()
        #resource_name = 'reminderdates'
        filtering = { 
            "id": ALL,
            "date": ALL,
            "nomcom": ALL_WITH_RELATIONS,
        }
api.nomcom.register(ReminderDatesResource())

from ietf.name.resources import NomineePositionStateNameResource
class NomineePositionResource(ModelResource):
    position         = ToOneField(PositionResource, 'position')
    nominee          = ToOneField(NomineeResource, 'nominee')
    state            = ToOneField(NomineePositionStateNameResource, 'state')
    class Meta:
        queryset = NomineePosition.objects.all()
        serializer = api.Serializer()
        #resource_name = 'nomineeposition'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "position": ALL_WITH_RELATIONS,
            "nominee": ALL_WITH_RELATIONS,
            "state": ALL_WITH_RELATIONS,
        }
api.nomcom.register(NomineePositionResource())

from ietf.name.resources import FeedbackTypeNameResource
from ietf.utils.resources import UserResource
class FeedbackResource(ModelResource):
    nomcom           = ToOneField(NomComResource, 'nomcom')
    type             = ToOneField(FeedbackTypeNameResource, 'type', null=True)
    user             = ToOneField(UserResource, 'user', null=True)
    positions        = ToManyField(PositionResource, 'positions', null=True)
    nominees         = ToManyField(NomineeResource, 'nominees', null=True)
    class Meta:
        queryset = Feedback.objects.all()
        serializer = api.Serializer()
        #resource_name = 'feedback'
        filtering = { 
            "id": ALL,
            "author": ALL,
            "subject": ALL,
            "comments": ALL,
            "time": ALL,
            "nomcom": ALL_WITH_RELATIONS,
            "type": ALL_WITH_RELATIONS,
            "user": ALL_WITH_RELATIONS,
            "positions": ALL_WITH_RELATIONS,
            "nominees": ALL_WITH_RELATIONS,
        }
api.nomcom.register(FeedbackResource())

from ietf.utils.resources import UserResource
class NominationResource(ModelResource):
    position         = ToOneField(PositionResource, 'position')
    nominee          = ToOneField(NomineeResource, 'nominee')
    comments         = ToOneField(FeedbackResource, 'comments')
    user             = ToOneField(UserResource, 'user')
    class Meta:
        queryset = Nomination.objects.all()
        serializer = api.Serializer()
        #resource_name = 'nomination'
        filtering = { 
            "id": ALL,
            "candidate_name": ALL,
            "candidate_email": ALL,
            "candidate_phone": ALL,
            "nominator_email": ALL,
            "time": ALL,
            "position": ALL_WITH_RELATIONS,
            "nominee": ALL_WITH_RELATIONS,
            "comments": ALL_WITH_RELATIONS,
            "user": ALL_WITH_RELATIONS,
        }
api.nomcom.register(NominationResource())

from ietf.person.resources import PersonResource
class FeedbackLastSeenResource(ModelResource):
    reviewer         = ToOneField(PersonResource, 'reviewer')
    nominee          = ToOneField(NomineeResource, 'nominee')
    class Meta:
        queryset = FeedbackLastSeen.objects.all()
        serializer = api.Serializer()
        filtering = {
            "id": ALL,
            "time": ALL,
            "reviewer": ALL_WITH_RELATIONS,
            "nominee": ALL_WITH_RELATIONS,
        }
api.nomcom.register(FeedbackLastSeenResource())
