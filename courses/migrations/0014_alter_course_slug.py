# Generated by Django 3.2.8 on 2022-01-30 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_course_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=models.CharField(max_length=50),
        ),
    ]
