from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student, SchoolFee, Accommodation
from django.contrib.auth.models import User

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
            # Only check for user existence after form submission
            if not User.objects.filter(username=username).exists():
                error = 'User not found'
            else:
                error = 'Invalid password'
    
    return render(request, 'login.html', {
        'error': error,
        'username': username
    })

@login_required
def dashboard_view(request):
    try:
        student = Student.objects.get(user=request.user)
        school_fee = SchoolFee.objects.filter(student=student).first()
        accommodation = Accommodation.objects.filter(student=student).first()
        
        context = {
            'student': {
                'id': student.student_id,
                'name': f"{student.user.first_name} {student.user.last_name}",
                'program': student.program,
                'level': student.level,
                'email': student.email
            },
            'finance': {
                'deposit': student.deposit_balance,
                'school_fees': {
                    'amount': school_fee.amount if school_fee else 0,
                    'status': school_fee.status if school_fee else 'pending',
                    'last_payment': school_fee.last_payment_date if school_fee else 'N/A',
                    'receipt': school_fee.receipt_number if school_fee else 'N/A'
                },
                'accommodation': {
                    'amount': accommodation.amount if accommodation else 0,
                    'status': accommodation.status if accommodation else 'pending',
                    'room': accommodation.room_number if accommodation else 'N/A',
                    'due_date': accommodation.due_date if accommodation else 'N/A'
                }
            }
        }
        return render(request, 'dashboard.html', context)
    except Student.DoesNotExist:
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')