# Generated by Django 5.1.7 on 2025-03-27 00:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=20, unique=True)),
                ('program', models.CharField(max_length=100)),
                ('level', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('deposit_balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SchoolFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('paid', 'Paid'), ('pending', 'Pending'), ('partial', 'Partial')], max_length=20)),
                ('last_payment_date', models.DateField(blank=True, null=True)),
                ('receipt_number', models.CharField(blank=True, max_length=50)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student_portal.student')),
            ],
        ),
        migrations.CreateModel(
            name='Accommodation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('paid', 'Paid'), ('pending', 'Pending')], max_length=20)),
                ('room_number', models.CharField(max_length=20)),
                ('due_date', models.DateField()),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='student_portal.student')),
            ],
        ),
    ]
