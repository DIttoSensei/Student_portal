from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    program = models.CharField(max_length=100)
    level = models.CharField(max_length=50)
    email = models.EmailField()
    
    # Financial Information
    deposit_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.student_id}"

class SchoolFee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('partial', 'Partial')
    ])
    last_payment_date = models.DateField(null=True, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)

class Accommodation(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('paid', 'Paid'),
        ('pending', 'Pending')
    ])
    room_number = models.CharField(max_length=20)
    due_date = models.DateField()