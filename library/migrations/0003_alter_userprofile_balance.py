# Generated by Django 5.0 on 2024-02-26 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
