# Generated by Django 3.2 on 2021-12-19 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0009_alter_message_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='date',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
