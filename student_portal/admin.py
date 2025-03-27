from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Student, SchoolFee, Accommodation

# Change admin site header
admin.site.site_header = "ESPAM Administration"
admin.site.site_title = "ESPAM Admin Portal"
admin.site.index_title = "Welcome to ESPAM Administration"

class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Details'

class CustomUserAdmin(UserAdmin):
    inlines = (StudentInline,)

class SchoolFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'status', 'last_payment_date')
    search_fields = ('student__user__username', 'student__student_id')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(SchoolFee, SchoolFeeAdmin)
admin.site.register(Accommodation)