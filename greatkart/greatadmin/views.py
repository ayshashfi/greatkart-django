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
# from orders.models import OrderProduct,Order,OrderStatus
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
   
     


