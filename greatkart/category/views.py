from django.shortcuts import render, redirect
import logging
from store.models import Product
# from variant.models import Variant,VariantImage
from .models import category
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import category
from django.http import Http404


@login_required(login_url='admin_login')
def categories(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    categories = category.objects.all().order_by('id')
    p=Paginator(categories,10)
    page=request.GET.get('page')
    product_page=p.get_page(page)
    page_nums='a'*product_page.paginator.num_pages
    context={
        'categories': categories,
        'product_page':product_page,
        'page_nums':page_nums,
        
    }
    return render(request, 'category/category.html',context )


@login_required(login_url='admin_login')
def add_category(request):
    try:
        if not request.user.is_superadmin:
            return redirect('admin_login')

        if request.method == 'POST':
            image = request.FILES.get('image', None)
            name = request.POST['category_name']
            description = request.POST['description']
            
            # Validation
            if name.strip() == '':
                messages.error(request, 'Name Not Found!')
                return redirect('categories')

            if category.objects.filter(category_name__iexact=name).exists():
                messages.error(request, 'Category name already exists')
                return redirect('categories')
            # Save
            if not image:
                messages.error(request, 'Image not uploaded')
                return redirect('categories')

            new_category = category(category_name=name, description=description, cat_image=image)
            new_category.save()
            messages.success(request,'category added successfully!')
            return redirect('categories')
    except:
            return redirect('categories')



@login_required(login_url='admin_login')
def edit_category(request, editcategory_id):
    if not request.user.is_superadmin:
        return redirect('admin_login')

    try:
        # Retrieve the category instance to be edited
        category_instance = category.objects.get(id=editcategory_id)

        if request.method == 'POST':
            # Process the form data if the request method is POST
            name = request.POST.get('category_name')
            description = request.POST.get('description')
            image = request.FILES.get('image', None)

            # Validation
            if name.strip() == '':
                messages.error(request, 'Name Not Found!')
                return redirect('categories')

            if category.objects.exclude(id=category_instance.id).filter(category_name=name).exists():
                messages.error(request, 'Category name already exists')
                return redirect('categories')

            # Save
            category_instance.category_name = name
            category_instance.description = description

            if image:
                category_instance.cat_image = image

            category_instance.save()
            messages.success(request, 'Category edited successfully!')
            return redirect('categories')

    except category.DoesNotExist:
        raise Http404("Category does not exist")  # Or redirect to an error page
    return render(request, 'edit_category.html', {'category_instance': category_instance})



@login_required(login_url='admin_login')
def deletecategory(request, deletecategory_id):
    if not request.user.is_superadmin:
        return redirect('admin_login')

    category_instance = category.objects.get(id=deletecategory_id)
    products = Product.objects.filter(category=category_instance)

    for product in products:
        product.is_available = False
        product.save()

    # variants = Variant.objects.filter(product=product)
    # for variant in variants:
    #     variant.is_available = False
    #     variant.quantity = 0
    #     variant.save()

    category_instance.delete()

    messages.success(request, 'Category deleted successfully!')
    return redirect('categories')



# @login_required(login_url='admin_login')
# def category_search(request):
#     search = request.POST.get('search')
#     if search is None or search.strip() == '':
#         messages.error(request,'Filed cannot empty!')
#         return redirect('categories')
#     categories = category.objects.filter(description__icontains=search )
#     if categories :
#         pass
#         return render(request, 'category/category.html', { 'categories': categories})
#     else:
#         categories:False
#         messages.error(request,'Search not found!')
#         return redirect('categories')

