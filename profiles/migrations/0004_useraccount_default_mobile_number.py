# Generated by Django 3.2.7 on 2022-01-04 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_auto_20220103_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='default_mobile_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
