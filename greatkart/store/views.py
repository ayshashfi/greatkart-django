from django.shortcuts import render,get_object_or_404,redirect,redirect
from .models import Product,Variation,ReviewRating
from category.models import category
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from .forms import ReviewForm
from orders.models import OrderProduct





# Create your views here.
def store(request,category_slug=None):
    categories=None
    products=None
    
    if category_slug!=None:
        categories=get_object_or_404(category,slug=category_slug)
        products=Product.objects.filter(category=categories)
        paginator=Paginator(products,1)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
    else:
        products=Product.objects.all().filter(is_available=True).order_by('id')
        paginator=Paginator(products,3)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count= products.count()
        
    
    
    context={
        'products':paged_products,
        'product_count':product_count,
    }
    
    return render(request,'store/store.html',context)




def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # Get the product gallery
    # product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        # 'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)



def search(request):
    if 'keyword' in request.GET:
        keyword=request.GET['keyword']
        if keyword:
            products=Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword)|    Q(product_name__icontains=keyword))
            product_count=products.count()
    context={
        'products':products,
        'product_count':product_count,
    }    
    return render(request,'store/store.html',context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
    
            
            



@login_required(login_url='admin_login')
def add_product(request):
    # Ensure only superadmins can access this view
    if not request.user.is_superadmin:
        return redirect('admin_login')

    if request.method == 'POST':
        name = request.POST.get('product_name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        product_description = request.POST.get('description')
        stock = request.POST.get('stock')
        image = request.FILES.get('images')  # Get the uploaded image file

        # Validation
        if not name or not price or not image:
            messages.error(request, "Name, Price, or Image field is empty!")
            return redirect('add_product')

        # Check if the product with the same name exists
        existing_product = Product.objects.filter(product_name=name).first()

        if existing_product:
            # If the existing product is not available, update its details
            if not existing_product.is_available:
                existing_product.price = price
                existing_product.category_id = category_id
                existing_product.description = product_description
                existing_product.stock = stock
                existing_product.is_available = True
                existing_product.images = image  # Update the image
                existing_product.save()
                messages.success(request, 'Product updated successfully!')
                return redirect('add_product')
            else:
                messages.error(request, 'Product name already exists')
                return redirect('add_product')

        # Create a new product
        try:
            category_obj = category.objects.get(id=category_id)
        except category.DoesNotExist:
            messages.error(request, 'Invalid category selected')
            return redirect('add_product')

        # Generate slug using Django's slugify function
        slug = slugify(name)

        # Save the product
        product = Product(
            product_name=name,
            category=category_obj,
            price=price,
            slug=slug,
            description=product_description,
            stock=stock,
            images=image  # Save the image
        )
        product.save()
        messages.success(request, 'Product added successfully!')
        return redirect('add_product')

    # For GET requests, render the form
    categories = category.objects.all()
    products = Product.objects.all()
    return render(request, 'store/product.html', {'categories': categories, 'products': products})



from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from .models import Product, category

@login_required(login_url='admin_login')
def edit_product(request, product_id):
    # Ensure only superadmins can access this view
    if not request.user.is_superadmin:
        return redirect('admin_login')

    # Get the product to edit or show an error if it doesn't exist
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        name = request.POST.get('product_name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        product_description = request.POST.get('description')
        stock = request.POST.get('stock')
        image = request.FILES.get('images')  # Get the uploaded image file

        # Validation
        if not name or not price or not image:
            messages.error(request, "Name, Price, or Image field is empty!")
            return redirect('edit_product', product_id=product.id)

        # Update the product details
        product.product_name = name
        product.price = price
        product.category_id = category_id
        product.description = product_description
        product.stock = stock
        product.images = image  # Update the image

        # Save the product
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('edit_product')

    # For GET requests, render the edit form
    categories = category.objects.all()
    return render(request, 'store/product.html', {'categories': categories, 'product': product})


# from django.shortcuts import render, get_object_or_404, redirect
# from .models import Product
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages

# @login_required(login_url='admin_login')
# def delete_product(request, product_id):
#     # Ensure only superadmins can access this view
#     if not request.user.is_superadmin:
#         return redirect('admin_login')

#     # Get the product to delete or show an error if it doesn't exist
#     product = get_object_or_404(Product, id=product_id)

#     if request.method == 'POST':
#         # Delete the product
#         product.delete()
#         messages.success(request, 'Product deleted successfully!')
#         return redirect('product')

#     # For GET requests, render the confirmation modal
#     return render(request, 'store/product.html', {'product': product})


@login_required(login_url='admin_login')
def delete_product(request, deleteproduct_id):
    if not request.user.is_superadmin:
        return redirect('admin_login')

    product_instance = Product.objects.get(id=deleteproduct_id)
    products = Product.objects.filter(product=product_instance)

    for product in products:
        product.is_available = False
        product.save()

    # variants = Variant.objects.filter(product=product)
    # for variant in variants:
    #     variant.is_available = False
    #     variant.quantity = 0
    #     variant.save()

    product_instance.delete()

    messages.success(request, 'Category deleted successfully!')
    return redirect('products')