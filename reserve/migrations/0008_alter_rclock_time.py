# Generated by Django 4.2.4 on 2023-09-04 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserve', '0007_studyroom_rclock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rclock',
            name='time',
            field=models.TimeField(),
        ),
    ]