# Generated by Django 3.2 on 2021-12-19 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0013_auto_20211219_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paper',
            name='doi',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]