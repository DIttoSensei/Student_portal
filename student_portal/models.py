from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    program = models.CharField(max_length=100)
    level = models.CharField(max_length=50)
    email = models.EmailField()
    deposit_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    enrollment_date = models.DateField(default=timezone.now)
    graduation_date = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['student_id']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    def make_payment(self, amount, payment_type, school_fee=None, accommodation=None, **kwargs):
        amount = Decimal(str(amount))
        if self.deposit_balance < amount:
            raise ValueError("Insufficient deposit balance")
        
        self.deposit_balance -= amount
        self.save()
        
        receipt_number = self.generate_receipt_number(payment_type)
        payment = Payment.objects.create(
            student=self,
            amount=amount,
            payment_type=payment_type,
            receipt_number=receipt_number,
            school_fee=school_fee,
            **kwargs
        )
        
        if payment_type == 'school_fee' and school_fee:
            school_fee.amount_paid = (school_fee.amount_paid or Decimal('0')) + amount
            school_fee.last_payment_date = timezone.now().date()
            school_fee.receipt_number = receipt_number
            school_fee.update_status()
            school_fee.save()
        
        if payment_type == 'accommodation' and accommodation:
            accommodation.amount_paid = (accommodation.amount_paid or Decimal('0')) + amount
            accommodation.payment_date = timezone.now().date()
            accommodation.receipt_number = receipt_number
            accommodation.update_status()
            accommodation.save()
        
        return payment
    
    def generate_receipt_number(self, payment_type):
        prefix = {'school_fee': 'SF', 'accommodation': 'AC', 'deposit': 'DP'}.get(payment_type, 'PY')
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"{prefix}-{self.student_id}-{timestamp}"

class SchoolFee(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('partial', 'Partial Payment'),
        ('pending', 'Pending'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='school_fees')
    academic_year = models.CharField(max_length=9)
    semester = models.CharField(max_length=20, choices=[
        ('first', 'First Semester'),
        ('second', 'Second Semester'),
        ('summer', 'Summer Semester'),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    last_payment_date = models.DateField(blank=True, null=True)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'academic_year', 'semester')
        ordering = ['-academic_year', 'semester']
    
    def __str__(self):
        return f"{self.student} - {self.academic_year} {self.get_semester_display()}"
    
    @property
    def balance(self):
        return self.amount - self.amount_paid
    
    def update_status(self):
        if self.amount_paid >= self.amount:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'
        self.save()

class Accommodation(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('partial', 'Partial Payment'),  # Added 'partial'
        ('pending', 'Pending'),
    ]
    
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='accommodation')
    room_number = models.CharField(max_length=20)
    hall_of_residence = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    payment_date = models.DateField(blank=True, null=True)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.student} - {self.hall_of_residence} {self.room_number}"
    
    @property
    def balance(self):
        return self.amount - self.amount_paid
    
    def update_status(self):
        if self.amount_paid >= self.amount:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'  # Added partial status
        else:
            self.status = 'pending'
        self.save()
    
    @property
    def is_overdue(self):
        return self.status != 'paid' and timezone.now().date() > self.due_date  # Updated to include partial

class Payment(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('school_fee', 'School Fee'),
        ('accommodation', 'Accommodation'),
        ('deposit', 'Deposit'),
        ('other', 'Other'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    date = models.DateTimeField(default=timezone.now)
    receipt_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    description = models.TextField(blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    
    school_fee = models.ForeignKey(SchoolFee, on_delete=models.SET_NULL, blank=True, null=True, related_name='payments')
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"{self.student} - {self.get_payment_type_display()} ({self.amount})"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.student.generate_receipt_number(self.payment_type)
        super().save(*args, **kwargs)

class Deposit(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='deposits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    reference = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=50, choices=[
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
        ('mobile_money', 'Mobile Money'),
        ('cash', 'Cash'),
    ])
    verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if self.verified and not self.pk:
            self.student.deposit_balance += self.amount
            self.student.save()
        super().save(*args, **kwargs)