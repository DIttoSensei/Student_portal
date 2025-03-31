from django.urls import path
from .views import login_view, dashboard_view, pay_school_fee, pay_accommodation, make_deposit, logout

urlpatterns = [
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout, name='logout'),
    path('pay/school-fee/', pay_school_fee, name='pay_school_fee'),
    path('pay/accommodation/', pay_accommodation, name='pay_accommodation'),
    
    path('deposit/', make_deposit, name='make_deposit'),
]