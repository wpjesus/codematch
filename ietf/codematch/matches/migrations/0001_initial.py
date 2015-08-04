# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '__first__'),
        ('doc', '0004_auto_20150403_1235'),
        ('person', '0004_auto_20150308_0440'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodingProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=80)),
                ('link_to_implementation', models.URLField(blank=True)),
                ('additional_information', models.CharField(max_length=255)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('reputation', models.IntegerField(null=True, blank=True)),
                ('coder', models.ForeignKey(blank=True, to='person.Person', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectContainer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=80)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('protocol', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('code_request', models.ForeignKey(blank=True, to='requests.CodeRequest', null=True)),
                ('codings', models.ManyToManyField(to='matches.CodingProject')),
                ('docs', models.ManyToManyField(to='doc.DocAlias')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
