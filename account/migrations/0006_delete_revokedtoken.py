# Generated by Django 5.1.5 on 2025-01-28 06:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "account",
            "0005_alter_userprofile_email_alter_userprofile_is_active_and_more",
        ),
    ]

    operations = [
        migrations.DeleteModel(
            name="RevokedToken",
        ),
    ]
