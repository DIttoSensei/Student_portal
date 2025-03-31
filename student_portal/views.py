from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum
from .models import Student, SchoolFee, Accommodation, Payment, Deposit
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

def login_view(request):
    error = None
    username = ''
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'User not found' if not User.objects.filter(username=username).exists() else 'Invalid password'
    
    return render(request, 'login.html', {'error': error, 'username': username})

@login_required
def dashboard_view(request):
    student = get_object_or_404(Student, user=request.user)
    school_fee = SchoolFee.objects.filter(student=student).first()
    accommodation = Accommodation.objects.filter(student=student).first()
    payments = Payment.objects.filter(student=student).order_by('-date')[:10]
    
    school_fee_data = {
        'amount': Decimal('0'),
        'amount_paid': Decimal('0'),
        'balance': Decimal('0'),
        'status': 'pending',
        'last_payment': 'N/A',
        'receipt': 'N/A'
    }
    if school_fee:
        school_fee_data = {
            'amount': school_fee.amount,
            'amount_paid': school_fee.amount_paid,
            'balance': school_fee.balance,
            'status': school_fee.status,
            'last_payment': school_fee.last_payment_date.strftime('%Y-%m-%d') if school_fee.last_payment_date else 'N/A',
            'receipt': school_fee.receipt_number or 'N/A'
        }
    
    accommodation_data = {
        'amount': Decimal('0'),
        'amount_paid': Decimal('0'),
        'balance': Decimal('0'),
        'status': 'pending',
        'room': 'N/A',
        'due_date': 'N/A'
    }
    if accommodation:
        accommodation_data = {
            'amount': accommodation.amount,
            'amount_paid': accommodation.amount_paid,
            'balance': accommodation.balance,
            'status': accommodation.status,
            'room': accommodation.room_number,
            'due_date': accommodation.due_date.strftime('%Y-%m-%d') if accommodation.due_date else 'N/A'
        }
    
    context = {
        'student': {
            'id': student.student_id,
            'name': f"{student.user.first_name} {student.user.last_name}",
            'program': student.program,
            'level': student.level,
            'email': student.email,
            'phone': student.phone_number or 'N/A',
            'address': student.address or 'N/A'
        },
        'finance': {
            'deposit': student.deposit_balance,
            'school_fees': school_fee_data,
            'accommodation': accommodation_data
        },
        'payments': [
            {
                'amount': p.amount,
                'type': p.get_payment_type_display(),
                'date': p.date.strftime('%Y-%m-%d %H:%M'),
                'receipt': p.receipt_number,
                'status': p.get_status_display()
            } for p in payments
        ]
    }
    return render(request, 'dashboard.html', context)

@require_POST
@login_required
def make_deposit(request):
    student = get_object_or_404(Student, user=request.user)
    
    try:
        amount = Decimal(request.POST.get('amount'))
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        
        Deposit.objects.create(
            student=student,
            amount=amount,
            payment_method='bank_transfer',
            reference=f"DEP-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            verified=True
        )
        messages.success(request, f"Deposit of ₦{amount:.2f} successful!")
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('dashboard')

@require_POST
@login_required
def pay_school_fee(request):
    student = get_object_or_404(Student, user=request.user)
    school_fee = get_object_or_404(SchoolFee, student=student)
    
    try:
        amount = Decimal(request.POST.get('amount'))
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        if amount > school_fee.balance:
            raise ValidationError(f"Cannot pay more than ₦{school_fee.balance:.2f}")
        if amount > student.deposit_balance:
            raise ValidationError("Insufficient deposit balance")
        
        with transaction.atomic():
            payment = student.make_payment(
                amount=amount,
                payment_type='school_fee',
                school_fee=school_fee
            )
            messages.success(request, f"Paid ₦{amount:.2f}. New balance: ₦{school_fee.balance:.2f}")
    
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('dashboard')

@require_POST
@login_required
def pay_accommodation(request):
    student = get_object_or_404(Student, user=request.user)
    accommodation = get_object_or_404(Accommodation, student=student)
    
    try:
        amount = Decimal(request.POST.get('amount'))
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        if amount > accommodation.balance:
            raise ValidationError(f"Cannot pay more than ₦{accommodation.balance:.2f}")
        if amount > student.deposit_balance:
            raise ValidationError("Insufficient deposit balance")
        
        with transaction.atomic():
            payment = student.make_payment(
                amount=amount,
                payment_type='accommodation',
                accommodation=accommodation
            )
            messages.success(request, f"Paid ₦{amount:.2f}. New balance: ₦{accommodation.balance:.2f}")
    
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('dashboard')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('login')