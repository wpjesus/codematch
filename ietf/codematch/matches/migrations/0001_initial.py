# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0002_auto_20150910_1119'),
        ('doc', '0004_auto_20150403_1235'),
        ('person', '0004_auto_20150308_0440'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodingProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=80)),
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
            name='ProjectContainer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=80)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('protocol', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('code_request', models.ForeignKey(blank=True, to='requests.CodeRequest', null=True)),
                ('codings', models.ManyToManyField(to='matches.CodingProject')),
                ('docs', models.ManyToManyField(to='doc.DocAlias')),
                ('owner', models.ForeignKey(blank=True, to='person.Person', null=True)),
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
