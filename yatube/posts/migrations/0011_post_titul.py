# Generated by Django 2.2.6 on 2023-06-04 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20230604_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='titul',
            field=models.TextField(default=1, help_text='Введите ключевое слово', verbose_name='Ключевое слово'),
            preserve_default=False,
        ),
    ]
