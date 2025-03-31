from django.db import migrations
from datetime import datetime

def fix_dates(apps, schema_editor):
    SchoolFee = apps.get_model('student_portal', 'SchoolFee')
    for fee in SchoolFee.objects.all():
        if fee.due_date:  # Skip if already null
            try:
                # Convert DD/MM/YYYY to date object
                day, month, year = map(int, str(fee.due_date).split('/'))
                fee.due_date = datetime(year, month, day).date()
                fee.save()
            except:
                fee.due_date = None
                fee.save()

class Migration(migrations.Migration):
    dependencies = [('student_portal', '0004_alter_schoolfee_due_date'),]  # Use your actual last migration number

    
    operations = [
        migrations.RunPython(fix_dates),
    ]