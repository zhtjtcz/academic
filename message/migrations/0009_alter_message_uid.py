# Generated by Django 3.2 on 2021-12-11 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0008_message_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='uid',
            field=models.IntegerField(default=0),
        ),
    ]
