# Generated by Django 2.2.3 on 2019-07-15 09:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('SOA', '0002_auto_20190715_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users',
                                    to='SOA.Address'),
        ),
    ]