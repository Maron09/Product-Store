# Generated by Django 5.1.6 on 2025-03-06 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0003_user_groups_user_is_admin_user_user_permissions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.PositiveSmallIntegerField(
                blank=True, choices=[(1, "Vendor"), (2, "Customer")], null=True
            ),
        ),
    ]
