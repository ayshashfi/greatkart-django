from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,Variation,ReviewRating,ProductGallery,Size,Color,VariantImage
from category.models import category
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from .forms import ReviewForm,ImageForm
from orders.models import OrderProduct
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import webcolors


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



from django.shortcuts import render, get_object_or_404


def product_detail(request, prod_id,img_id):
    variant = VariantImage.objects.filter(variant=img_id,is_available=True)
    variant_images = (VariantImage.objects.filter(variant__product__id=prod_id,is_available=True)
                     .distinct('variant__product'))
    size =VariantImage.objects.filter(variant__product__id=prod_id).distinct('variant__size')
    size =Size.objects.filter(is_available=True)
    color=VariantImage.objects.filter(variant__product__id=prod_id,is_available=True).distinct('variant__color')
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=variant).exists()
  

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=variant.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=prod_id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=prod_id)

    context = {
        'variant':variant,
        'size':size,
        'color':color,
        'in_cart'       : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
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
def products(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    product=Product.objects.all()
    p=Paginator(product,5)
    page=request.GET.get('page')
    product_page=p.get_page(page)
    page_nums='a'*product_page.paginator.num_pages

    product_list={
        'product':product,
        'categories':category.objects.filter(is_available=True).order_by('id'),
        'product_page':product_page,
        'page_nums':page_nums,
        
    }

    return render (request,'store/product.html',product_list)

@login_required(login_url='admin_login')
def product_view(request,product_id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    variant=Variation.objects.filter(product=product_id,is_available=True)
    size_range=Size.objects.filter(is_available=True).order_by('id')
    color_name=Color.objects.filter(is_available=True).order_by('id')
    product=Product.objects.filter(is_available=True).order_by('id')

    variant_list={
        'variant':variant,
        'size_range':size_range,
        'color_name':color_name,
        'product':product

    }

    return render(request,'store/product_view.html',{'variant_list':variant_list})
            


@login_required(login_url='admin_login')
def addproduct(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    if request.method == 'POST':
        name = request.POST['product_name']
        price = request.POST['product_price']
        category_id = request.POST.get('category')
        # offer_id = request.POST.get('offer')
        product_description = request.POST.get('description')
        # Validation
        if Product.objects.filter(product_name=name).exists():
            check = Product.objects.get(product_name=name)
            if check.is_available == False:
                check.product_name +=check.product_name
                check.slug +=check.slug
                check.save()
            else:    
                messages.error(request, 'Product name already exists')
                return redirect('products')
      
        if name.strip() == '' or price.strip() == '':
            messages.error(request, "Name or Price field are empty!")
            return redirect('products')
       
        category_obj = category.objects.get(id=category_id)
        # if offer_id == '':
        #     offer_obj=None
        # else:    
        #     offer_obj = Offer.objects.get(id=offer_id)
        
       
        # Save        
        product = Product(
          
            product_name=name,
            category=category_obj,
            # offer=offer_obj,
            product_price=price,
            slug=name,
            description=product_description,
        )
        product.save()
        messages.success(request,'product added successfully!')
        return redirect('products')
    
    return render(request, 'store/product.html')

@login_required(login_url='admin_login')
def product_edit(request,product_id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    if request.method=='POST':
        name=request.POST['product_name']
        price=request.POST['product_price']
        category_id=request.POST.get('category')
        # offer_id=request.POST.get('offer')
        product_description = request.POST.get('description', '')


        if name.strip()=='' or price.strip()=='':
            messages.error(request,'Fields cannot be empty!')
            return redirect('products')
        
        category_obj= category.objects.get(id=category_id)
        # if offer_id=='':
        #     offer_id=None
        # else:
        #     offer_obj=Offer.objects.get(id=offer_id)   

        if Product.objects.filter(product_name=name).exists():
            check=Product.objects.get(id=product_id)
            if name==check.product_name:
                pass
            else:
                messages.error(request,'Product name already exists!')
                return redirect('products')

        editproduct=Product.objects.get(id=product_id)
        editproduct.product_name=name
        editproduct.product_price=price
        editproduct.category=category_obj
        # editproduct.offer=offer_obj
        editproduct.description=product_description
        editproduct.save()
        messages.success(request,'Product edited successfully!')
        return redirect('products')
    
    
@login_required(login_url='admin_login')
def product_delete(request,product_id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    delete_product=Product.objects.get(id=product_id)
    variants=Variation.objects.filter(product=delete_product)
    if delete_product.is_available:
        for variant in variants:
            variant.is_available= False
            variant.quantity=0
            variant.save()
        delete_product.is_available=False
        delete_product.save()
        messages.success(request,'product deleted successfully!')
    else:
        for variant in variants:
            variant.is_available= True
            variant.quantity=0
            variant.save()
        delete_product.is_available=True
        delete_product.save()
        messages.success(request,'product added successfully!')
    return redirect('products') 



@login_required(login_url='admin_login')
def product_variant(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    variant = Variation.objects.all()
    size_range= Size.objects.all()
    color_name= Color.objects.all()
    product=Product.objects.all()
    p=Paginator(variant,8)
    page=request.GET.get('page')
    variant_page=p.get_page(page)
    page_nums='a'*variant_page.paginator.num_pages
    variant_list={
        'variant'    :variant,
        'size_range' :size_range,
        'color_name' :color_name, 
        'product'   :product,
        'variant_page':variant_page,
        'page_nums':page_nums,
    }
    return render(request,'variant/variant.html',{'variant_list':variant_list}) 


@login_required(login_url='admin_login')  
def add_Product_Variant(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')

    if request.method == 'POST':
        variant_name = request.POST.get('variant_name')
        variant_size = request.POST.get('variant_size')
        variant_color = request.POST.get('variant_color')
        variant_quantity = request.POST.get('variant_quantity')

        # Validation
        if variant_quantity.strip() == '':
            messages.error(request, "Quantity field is empty!")
            return redirect('product_variant')

        try:
            product_obj = Product.objects.get(id=variant_name)
            size_obj = Size.objects.get(id=variant_size)
            color_obj = Color.objects.get(id=variant_color)

            # Check if variant already exists
            if Variation.objects.filter(product=product_obj, size=size_obj, color=color_obj).exists():
                messages.error(request, "Variant with the same product, size, and color already exists!")
                return redirect('product_variant')

            # Save new variant
            add_variant = Variation(
                product=product_obj,
                color=color_obj,
                size=size_obj,
                quantity=variant_quantity,
            )
            add_variant.save()

            messages.success(request, 'Variant added successfully!')
            return redirect('product_variant')

        except ObjectDoesNotExist:
            messages.error(request, "Invalid product, size, or color selected!")
            return redirect('product_variant')

    return render(request, 'variant/variant.html')
 
@login_required(login_url='admin_login')  
def edit_productvariant(request,variant_id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    if request.method == 'POST':
        variant_name = request.POST.get('variant_name')
        variant_size = request.POST.get('variant_size')
        variant_color = request.POST.get('variant_color')
        variant_quantity = request.POST.get('variant_quantity')
        
        if variant_quantity.strip() == '':
            messages.error(request, "Quantity field is empty!")
            return redirect('product_variant')
        
     
        product_obj = Product.objects.get(id=variant_name)
        size_obj = Size.objects.get(id=variant_size)
        color_obj = Color.objects.get(id=variant_color)

        # Check if variant already exists
        if Variation.objects.filter(product=product_obj, size=size_obj, color=color_obj).exists():
            check = Variation.objects.get(id=variant_id)
            if product_obj==check.product and size_obj==check.size and color_obj==check.color:
                pass
            else:
                messages.error(request, "Variant with the same product, size, and color already exists!")
                return redirect('product_variant')
        
        edit_variant=Variation.objects.get(id=variant_id)
        edit_variant.color=color_obj
        edit_variant.size=size_obj
        edit_variant.product=product_obj
        edit_variant.quantity=variant_quantity
        edit_variant.save()
        messages.success(request,'product edited successfully!')
        
        return redirect('product_variant')
    
    
@login_required(login_url='admin_login')              
def productvariant_delete(request, variant_id):  
    if not request.user.is_superadmin:
        return redirect('admin_login')
    delete_productvariant = Variation.objects.get(id=variant_id) 
    if delete_productvariant.is_available:
        delete_productvariant.is_available =False
        delete_productvariant.quantity= 0
        delete_productvariant.save()
        messages.success(request,'product_variant deleted successfully!')
    else:
        delete_productvariant.is_available =True
        delete_productvariant.quantity= 0
        delete_productvariant.save()
        messages.success(request,'product_variant added successfully!')
        
    return redirect('product_variant')   


@login_required(login_url='admin_login')  
def image_list(request,variant_id):  
    image=VariantImage.objects.filter(variant=variant_id,is_available =True)
    add_image =variant_id
    return render(request,'variant/image_management.html',{'image':image,'add_image':add_image})

#  This is image add function         
def image_view(request, img_id):
    
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        var = Variation.objects.get(id=img_id)

        if form.is_valid():
            image_instance = form.save(commit=False)  
            image_instance.variant = var  
            image_instance.save()  

            print("Image saved successfully!")
            
            
            return JsonResponse({'message': 'works','img_id':img_id})
            
        else:
            print("Form is not valid:", form.errors)
            
    else:
        form = ImageForm()
    
    context = {'form': form,'img_id':img_id}
    return render(request, 'variant/image_add.html', context)

@login_required(login_url='admin_login')  
def image_delete(request, image_id):  
    if not request.user.is_superadmin:
        return redirect('admin_login')
    try:
        delete_image =VariantImage.objects.get(id=image_id)
        var_id= delete_image.variant.id 
        delete_image.is_available=False
        delete_image.save()
        messages.success(request,'image deleted successfully!')
        image=VariantImage.objects.filter(variant=var_id, is_available=True)
        add_image =var_id
        return render(request,'variant/image_management.html',{'image':image,'add_image':add_image})
    except:
           return redirect('product_variant') 
       
       
@login_required(login_url='admin_login')         
def product_variant_view(request,product_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
  
    variant=VariantImage.objects.filter(variant__product=product_id ,is_available=True)
    size_range= Size.objects.filter(is_available=True).order_by('id')
    color_name= Color.objects.filter(is_available=True).order_by('id')
    product=Product.objects.filter(is_available=True).order_by('id')
    variant_list={
        'variant'    :variant,
        'size_range' :size_range,
        'color_name' :color_name, 
         'product'   :product,
         
    }
    # variant_id
    return render(request,'variant/variant_view.html',{'variant_list':variant_list})


@login_required(login_url='admin_login1')  
def variant_search(request):
    search = request.POST.get('search')
    if search is None or search.strip() == '':
        messages.error(request,'Filed cannot empty!')
        return redirect('product_variant')
    variant = Variation.objects.filter( Q(product__product_name__icontains=search) | Q(color__color_name__icontains=search) |Q(size__size_range__icontains=search)| Q(quantity__icontains=search), is_available=True) 
    size_range= Size.objects.filter(is_available=True).order_by('id')
    color_name= Color.objects.filter(is_available=True).order_by('id')
    product=Product.objects.filter(is_available=True).order_by('id')
    variant_list={
        'variant'    :variant,
        'size_range' :size_range,
        'color_name' :color_name, 
         'product'   :product,
    }
    if variant :
        pass
        return render(request,'variant/variant.html',{'variant_list':variant_list}) 
    else:
        variant:False
        messages.error(request,'Search not found!')
        return redirect('product_variant') 
    
    
@login_required(login_url='admin_login')      
def product_size(request):
    if not request.user.is_superadmin:
            return redirect('admin_login')   
    products_size=Size.objects.filter(is_available =True).order_by('id')
    p=Paginator(products_size,4)
    page=request.GET.get('page')
    size_page=p.get_page(page)
    page_nums='a'*size_page.paginator.num_pages
    return render(request,'variant/size_management.html',{'products_size':products_size,'size_page':size_page,'page_nums':page_nums})

@login_required(login_url='admin_login')  
def add_size(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')

    if request.method == 'POST':
        size = request.POST.get('size')  
        if  size.strip() == '':
            messages.error(request, 'Field cannot be empty!')
            return redirect('product_size')

        if Size.objects.filter(size_range=size).exists():
            messages.error(request, 'Size already exists')
            return redirect('product_size')

        size_object = Size(size_range=size)
        size_object.save()
        messages.success(request,'Size added successfully!')
        return redirect('product_size')

    return render(request, 'variant/size_management.html')

@login_required(login_url='admin_login')  
def size_delete(request, size_range_id):  
    if not request.user.is_superadmin:
        return redirect('admin_login')
    delete_size = Size.objects.get(id=size_range_id) 
    delete_size.is_available=False
    delete_size.save()
    messages.success(request,'Size deleted successfully!')
    return redirect('product_size') 

def product_color(request):
    if not request.user.is_superadmin:
            return redirect('admin_login')   
    products_color=Color.objects.filter(is_available=True).order_by('id')
    p=Paginator(products_color,5)
    page=request.GET.get('page')
    color_page=p.get_page(page)
    page_nums='a'*color_page.paginator.num_pages
    return render(request,'variant/color_management.html',{'products_color':products_color,'color_page':color_page,'page_nums':page_nums})

def get_color_name(color_code):
    try:
        color_name = webcolors.rgb_to_name(webcolors.hex_to_rgb(color_code))
        return color_name
    except ValueError:
        return "Unknown"
    
def add_color(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')

    if request.method == 'POST':
        colorname = request.POST.get('color1')  
        color = request.POST.get('color')  
        color1=color
        
        color= get_color_name(color)
        if color == "Unknown":
            color=color1
        
        if colorname.strip() == '':
            messages.error(request, 'Field cannot be empty!')
            return redirect('product_color')

        if Color.objects.filter(color_name=colorname).exists():
            color_add =Color.objects.get(color_name=colorname)
            if color_add.is_available ==False:
                pass
            else:
                messages.error(request, 'color already exists!')
                return redirect('product_color')

        color_object = Color(color_name=colorname,color_code=color)
        color_object.save()
        
        messages.success(request,'color add successfully!')

        return redirect('product_color')

    return render(request, 'color_management/color_management.html')


def color_delete(request, color_name_id):  
    if not request.user.is_superadmin:
        return redirect('admin_login')
    delete_color =Color.objects.get(id=color_name_id) 
    delete_color.is_available =False
    delete_color.save()
    messages.success(request,'color deleted successfully!')
    return redirect('product_color')