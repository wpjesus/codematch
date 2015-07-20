# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='codingproject',
            old_name='Additional_Information',
            new_name='additional_information',
        ),
        migrations.RenameField(
            model_name='codingproject',
            old_name='User',
            new_name='coder',
        ),
        migrations.RenameField(
            model_name='codingproject',
            old_name='time',
            new_name='creation_date',
        ),
        migrations.RenameField(
            model_name='codingproject',
            old_name='Link_to_Implementation',
            new_name='link_to_implementation',
        ),
        migrations.RenameField(
            model_name='codingproject',
            old_name='ProjectContainer',
            new_name='project_container',
        ),
        migrations.RenameField(
            model_name='codingproject',
            old_name='Title',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='projectcontainer',
            old_name='CodeRequest',
            new_name='code_request',
        ),
        migrations.RenameField(
            model_name='projectcontainer',
            old_name='Person',
            new_name='coder',
        ),
        migrations.RenameField(
            model_name='projectcontainer',
            old_name='Creation_date',
            new_name='creation_date',
        ),
        migrations.RenameField(
            model_name='projectcontainer',
            old_name='Description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='projectcontainer',
            old_name='Protocol',
            new_name='protocol',
        ),
        migrations.RenameField(
            model_name='projectcontainer',
            old_name='Title',
            new_name='title',
        ),
    ]
