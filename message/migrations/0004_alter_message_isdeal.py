# Generated by Django 3.2 on 2021-12-07 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0003_message_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='isdeal',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
