# Generated by Django 5.1.7 on 2025-03-28 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_portal', '0006_fix_date_formats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolfee',
            name='due_date',
            field=models.DateField(default='2025-03-10'),
            preserve_default=False,
        ),
    ]
