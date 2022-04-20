# Generated by Django 2.2.9 on 2022-04-19 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Выберите группу для поста(необязательно)', null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.Group', verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(default='-пусто-', help_text='Введите текст', verbose_name='Текст поста'),
        ),
    ]
