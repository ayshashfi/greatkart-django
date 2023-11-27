from django.shortcuts import render
from django.contrib import messages,auth
from itertools import groupby
from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from accounts.models import *
from django.db.models import Q
# from products.models import ProductReview
from accounts.models import Account,MyAccountManager
from orders.models import OrderProduct,Order,OrderStatus
from django.db.models import Sum,Prefetch
from datetime import datetime,date
import csv
# from django import FPDF
from django.core.paginator import Paginator



def admin_login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        
        if email.strip()=='' or password.strip()=='':
            messages.error(request,'fields cannot be empty!')
            return redirect('admin_login')
        
        user=auth.authenticate(email=email,password=password)
        
        if user is not None:
            
            if user.is_active:
               if user.is_superadmin:
                    auth.login(request,user)
                    return redirect('admin_dashboard')
               else:
                    messages.warning(request,'Sorry only admin is allowed to login! ')
                    return redirect('admin_login')
            else:
               messages.warning(request,"Your account has been blocked!")
               return redirect('admin_login')

        else:
            messages.error(request,'Invalid username or password!')
            return redirect('admin_login')
    return render(request,'admin/admin_login.html')
   
     

def admin_dashboard(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    sales_data = OrderProduct.objects.values('order__created_at__date').annotate(total_sales=Sum('product_price')).order_by('-order__created_at__date')
    # Prepare data for the chart
    categories = [item['order__created_at__date'].strftime('%d/%m') for item in sales_data]
    sales_values = [item['total_sales'] for item in sales_data]
    return_data = OrderProduct.objects.filter(orderitem_status__item_status__in=["Return", "Cancelled"]).values('order__created_at__date').annotate(total_returns=Sum('product_price')).order_by('-order__created_at__date')
    return_values = [item['total_returns'] for item in return_data]
    orders =Order.objects.order_by('-created_at')[:10]
    try:
        totalsale=0
        total_sales =Order.objects.all()
        for i in total_sales:
            i.total_price
            totalsale+=i.total_price
    except:
         totalsale=0 
    try:
        totalearnings=0
        total_earn =Order.objects.filter(order_status__id=4)
        for i in total_earn:
            i.total_price
            totalearnings+=i.total_price
    except:
         totalearnings=0       
        
    try:
        status_pending_count=Order.objects.filter(order_status__id=1).count()
        status_delivery_count=Order.objects.filter(order_status__id=4).count()
        status_cancel_count =Order.objects.filter(order_status__id=5).count()
        status_return_count =Order.objects.filter(order_status__id=6).count()
        Total = status_delivery_count + status_cancel_count + status_return_count
        status_delivery = (status_delivery_count / Total) * 100
        status_cancel = (status_cancel_count / Total) * 100
        status_return = (status_return_count / Total) * 100
    except:
       
        status_delivery=0
        status_cancel=0
        status_return=0
        
            
    context = {
        'delivery_count':status_delivery_count,
        'cancel_count':status_cancel_count,
        'pending_count':status_pending_count,
        'totalsale':totalsale,
        'totalearnings':totalearnings,
        'status_delivery':status_delivery,
        'status_cancel':status_cancel,
        'status_return':status_return,
        'orders':orders,
        'categories': categories,
        'sales_values': sales_values,
        'return_values': return_values,
    }
    
    
    return render(request,'admin/admin_dashboard.html',context)
