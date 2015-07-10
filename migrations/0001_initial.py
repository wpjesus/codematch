# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0004_auto_20150403_1235'),
        ('person', '0004_auto_20150308_0440'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Estimated_LoF', models.CharField(max_length=80)),
                ('Additional_information', models.CharField(max_length=255)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to='person.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CodingProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Title', models.CharField(max_length=80)),
                ('Link_to_Implementation', models.URLField(blank=True)),
                ('Additional_Information', models.CharField(max_length=255)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectContainer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Title', models.CharField(max_length=80)),
                ('Creation_date', models.DateTimeField(auto_now_add=True)),
                ('Protocol', models.CharField(max_length=255)),
                ('Description', models.CharField(max_length=255)),
                ('CodeRequest', models.ForeignKey(blank=True, to='codematch.CodeRequest', null=True)),
                ('docs', models.ManyToManyField(to='doc.DocAlias')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='codingproject',
            name='ProjectContainer',
            field=models.ForeignKey(blank=True, to='codematch.ProjectContainer', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='codingproject',
            name='User',
            field=models.ForeignKey(blank=True, to='person.Person', null=True),
            preserve_default=True,
        ),
    ]
