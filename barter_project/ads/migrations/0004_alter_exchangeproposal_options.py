# Generated by Django 5.2.1 on 2025-05-17 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0003_alter_ad_description_alter_ad_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exchangeproposal',
            options={'ordering': ['-created_at']},
        ),
    ]
