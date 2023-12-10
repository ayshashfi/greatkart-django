from django.shortcuts import render
from django.contrib import messages,auth
from .forms import AdminForm, AdminProfileForm
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from accounts.models import *
from greatadmin.models import *
from django.db.models import Q
from accounts.models import Account,MyAccountManager
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


@login_required(login_url='admin_login')
def usermanagement(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    users = Account.objects.filter(is_superadmin=False).order_by('id')
    p=Paginator(users,6)
    page=request.GET.get('page')
    user_page=p.get_page(page)
    page_nums='a'*user_page.paginator.num_pages
    context={
        'users':users,
        'user_page':user_page,
        'page_nums':page_nums
        }
    return render(request,'admin/usermanagement.html',context)



@login_required(login_url='admin_login')   
def blockuser(request,user_id):
    
    if not request.user.is_superadmin:
        return redirect('admin_login')
    user =Account.objects.get(id=user_id)
    if user.is_active:
        user.is_active = False
        user.save()  
    else:
        user.is_active = True
        user.save()
    return redirect('usermanagement')



@login_required(login_url='admin_login')
def edit_admin_profile(request):
    try:
        adminprofile = AdminProfile.objects.get(user=request.user)
    except AdminProfile.DoesNotExist:
        # If AdminProfile does not exist, create a new one
        adminprofile = AdminProfile(user=request.user)

    if request.method == 'POST':
        admin_form = AdminForm(request.POST, instance=request.user)
        profile_form = AdminProfileForm(request.POST, request.FILES, instance=adminprofile)

        if admin_form.is_valid() and profile_form.is_valid():
            admin_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_admin_profile')
    else:
        admin_form = AdminForm(instance=request.user)
        profile_form = AdminProfileForm(instance=adminprofile)

    context = {
        'admin_form': admin_form,
        'profile_form': profile_form,
        'userprofile': adminprofile,
    }
    return render(request, 'admin/edit_admin_profile.html', context)



@login_required(login_url='admin_login')
def admin_logout1(request):
    logout(request)
    return redirect('admin_login')