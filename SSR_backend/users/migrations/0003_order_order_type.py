# Generated by Django 3.0.4 on 2021-01-04 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_type',
            field=models.CharField(default='other', max_length=64, verbose_name='order type'),
        ),
    ]
