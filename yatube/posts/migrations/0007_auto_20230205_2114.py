# Generated by Django 2.2.16 on 2023-02-05 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_follow'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follow',
            old_name='following',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='follow',
            old_name='follower',
            new_name='user',
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='follow',
            name='follow_time',
        ),
    ]