# Generated by Django 4.2.4 on 2023-09-05 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserve', '0008_alter_rclock_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rclock',
            name='time',
            field=models.CharField(max_length=15),
        ),
    ]
