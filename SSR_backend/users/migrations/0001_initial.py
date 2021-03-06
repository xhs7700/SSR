# Generated by Django 3.0.4 on 2020-12-30 08:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='User name')),
                ('psw', models.CharField(max_length=256, verbose_name='password')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('has_confirmed', models.BooleanField(default=False)),
                ('auth', models.CharField(default='consumer', max_length=64, verbose_name='authority')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='place name')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='users.User')),
            ],
            options={
                'verbose_name': 'Place',
                'verbose_name_plural': 'Places',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='device name')),
                ('status', models.CharField(default='offline', max_length=32, verbose_name='device status')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('changed_time', models.DateTimeField(auto_now=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Place')),
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
                'ordering': ['location'],
            },
        ),
        migrations.CreateModel(
            name='ConfirmString',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=256, verbose_name='confirm code')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.User')),
            ],
            options={
                'verbose_name': 'Confirm Code',
                'verbose_name_plural': 'Confirm Codes',
                'ordering': ['-created_time'],
            },
        ),
    ]
