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
from store.models import Product
from orders.models import OrderProduct,Order
from django.db.models import Sum,Prefetch
from datetime import datetime,date
import csv
# from django import FPDF
from django.core.paginator import Paginator


def admin_login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        
        user=auth.authenticate(email=email,password=password)
        
        if email.strip()=='' or password.strip()=='':
            messages.error(request,'fields cannot be empty!')
            return redirect('admin_login')
        
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

   
@login_required(login_url='admin_login')
def admin_dashboard(request):
    # # for cards on dashboard
    
    # customercount=Account.objects.all().count()
    # productcount=Product.objects.all().count()
    # ordercount=Order.objects.all().count()
    
    # for recent order tables
    # orders=Order.objects.all()
    # ordered_products=[]
    # ordered_bys=[]
    # for order in orders:
    #     ordered_product=Product.objects.all().filter(id=order.product.id)
    #     ordered_by=Account.objects.all().filter(id = order.user.id)
    #     ordered_products.append(ordered_product)
    #     ordered_bys.append(ordered_by)

    # mydict={
    # 'customercount':customercount,
    # 'productcount':productcount,
    # 'ordercount':ordercount,
    # 'data':zip(ordered_products,ordered_bys,orders),
    # }
    # return render(request,'admin/admin_dashboard.html',context=mydict)
    return render(request,'admin/admin_dashboard.html')
