# Generated by Django 2.2.6 on 2023-06-04 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_post_titul'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='titul',
            field=models.CharField(help_text='Введите ключевое слово', max_length=100, verbose_name='Ключевое слово'),
        ),
    ]
