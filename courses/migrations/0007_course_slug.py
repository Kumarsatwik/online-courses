# Generated by Django 3.2.8 on 2022-01-30 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_remove_course_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='slug',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
