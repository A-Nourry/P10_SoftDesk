# Generated by Django 4.1.1 on 2022-09-29 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contributors",
            name="permission",
            field=models.CharField(default=1, max_length=128, verbose_name="rôle"),
            preserve_default=False,
        ),
    ]
