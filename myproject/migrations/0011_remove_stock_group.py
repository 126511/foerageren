# Generated by Django 3.2.8 on 2021-12-02 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myproject', '0010_stock_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='group',
        ),
    ]