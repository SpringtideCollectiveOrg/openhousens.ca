# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legislature', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='bill',
            field=models.ForeignKey(null=True, blank=True, to='legislature.Bill'),
            preserve_default=True,
        ),
    ]
