# Autogenerated by the mkresources management command 2014-11-13 23:53
from tastypie.resources import ModelResource
from tastypie.fields import ToOneField, ToManyField
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from ietf import api

from ietf.message.models import *       # pyflakes:ignore


from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
from ietf.doc.resources import DocumentResource
class MessageResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    related_groups   = ToManyField(GroupResource, 'related_groups', null=True)
    related_docs     = ToManyField(DocumentResource, 'related_docs', null=True)
    class Meta:
        queryset = Message.objects.all()
        #resource_name = 'message'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "subject": ALL,
            "frm": ALL,
            "to": ALL,
            "cc": ALL,
            "bcc": ALL,
            "reply_to": ALL,
            "body": ALL,
            "content_type": ALL,
            "by": ALL_WITH_RELATIONS,
            "related_groups": ALL_WITH_RELATIONS,
            "related_docs": ALL_WITH_RELATIONS,
        }
api.message.register(MessageResource())

from ietf.person.resources import PersonResource
class SendQueueResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    message          = ToOneField(MessageResource, 'message')
    class Meta:
        queryset = SendQueue.objects.all()
        #resource_name = 'sendqueue'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "send_at": ALL,
            "sent_at": ALL,
            "note": ALL,
            "by": ALL_WITH_RELATIONS,
            "message": ALL_WITH_RELATIONS,
        }
api.message.register(SendQueueResource())
