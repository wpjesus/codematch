# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodingProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=80)),
                ('additional_information', models.CharField(max_length=255)),
                ('coder', models.IntegerField(null=True, blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('reputation', models.IntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Implementation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.URLField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact', models.CharField(max_length=80)),
                ('type', models.CharField(max_length=50, choices=[(b'Twitter', b'Twitter'), (b'Facebook', b'Facebook'), (b'Jabber', b'Jabber'), (b'Mail', b'Email')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectContainer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner', models.IntegerField(null=True, blank=True)),
                ('title', models.CharField(max_length=80)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('protocol', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('docs', models.CommaSeparatedIntegerField(max_length=200, null=True, blank=True)),
                ('code_request', models.ForeignKey(blank=True, to='requests.CodeRequest', null=True)),
                ('codings', models.ManyToManyField(to='matches.CodingProject')),
                ('contacts', models.ManyToManyField(to='matches.ProjectContact', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='projectcontainer',
            name='tags',
            field=models.ManyToManyField(to='matches.ProjectTag', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='codingproject',
            name='links',
            field=models.ManyToManyField(to='matches.Implementation', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='codingproject',
            name='tags',
            field=models.ManyToManyField(to='matches.ProjectTag', null=True, blank=True),
            preserve_default=True,
        ),
    ]
