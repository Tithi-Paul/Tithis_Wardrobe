from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating
from category.models import Category
from cart.models import CartItem
from django.db.models import Q

from cart.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages
from django.db.models import Avg, Count

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
        product_count = products.count()

    context = {
        'products': paged_products,
        'p_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        orderproduct = True
    else:
        orderproduct = None
        
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
    }
    return render(request, 'store/product_details.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'p_count': product_count,
    }
    return render(request, 'store/store.html', context)

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
            
def searchBySize(request, id):
    if id == 1:
        keyword = 'sm'
    elif id == 2:
        keyword = 'lg'
    elif id == 3:
        keyword = 'xl'
    elif id == 4:
        keyword = 'xxl'

    if keyword:
        products = Product.objects.order_by('-created_date').filter(size=keyword)
        product_count = products.count()
    context = {
        'products': products,
        'p_count': product_count,
    }
    return render(request, 'store/store.html', context)

def searchByColor(request, id):
    if id == 1:
        keyword = 'red'
    elif id == 2:
        keyword = 'blue'
    elif id == 3:
        keyword = 'green'
    elif id == 4:
        keyword = 'black'
    elif id == 5:
        keyword = 'white'

    if keyword:
        products = Product.objects.order_by('-created_date').filter(Q(color__icontains=keyword))
        product_count = products.count()
    context = {
        'products': products,
        'p_count': product_count,
    }
    return render(request, 'store/store.html', context)

def sortBy(request, id):
    if id == 1:
        products = Product.objects.order_by('price').reverse
    elif id == 2:
        products = Product.objects.order_by('price')
    elif id == 3:
        products = Product.objects.order_by('popularity').reverse
    elif id == 4:
        products = Product.objects.order_by('popularity')

    print(products)

    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)