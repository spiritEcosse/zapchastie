# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oscar.models.fields
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MetaTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meta_title', models.CharField(max_length=480, verbose_name='Meta tag: title')),
                ('h1', models.CharField(max_length=310, verbose_name='h1')),
                ('meta_description', models.TextField(verbose_name='Meta tag: description')),
                ('meta_keywords', models.TextField(verbose_name='Meta tag: keywords')),
                ('page_url', oscar.models.fields.ExtendedURLField(unique=True, max_length=128, verbose_name='Page URL', verify_exists=True)),
            ],
            options={
                'verbose_name': 'Meta tags on page',
                'verbose_name_plural': 'Meta tags on pages',
            },
        ),
    ]
