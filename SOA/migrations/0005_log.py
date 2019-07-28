# Generated by Django 2.2.3 on 2019-07-22 06:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('SOA', '0004_auto_20190716_1115'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.CharField(choices=[('+', 'Add'), ('-', 'Remove'), ('*', 'Update')], max_length=1)),
                ('operand', models.CharField(max_length=20)),
                ('operand_object', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('fields', models.CharField(max_length=256, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
