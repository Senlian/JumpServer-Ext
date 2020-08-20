# Generated by Django 2.2.10 on 2020-07-09 06:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orgs', '0003_auto_20190916_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='cies',
            field=models.ManyToManyField(blank=True, related_name='related_cie_orgs', to=settings.AUTH_USER_MODEL),
        ),
    ]
