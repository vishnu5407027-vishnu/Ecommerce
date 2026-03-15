from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

#paginator
from django.core.paginator import Paginator


# shop/views.py
from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request):
    products = Product.objects.filter(is_active=True)[:12]
    recommended_products = Product.objects.filter(is_active=True).order_by('?')[:12]
    categories = Category.objects.all()

    return render(request, 'product_list.html', {
        'products': products,
        'recommended_products': recommended_products,
        'categories': categories
    })

def best_deals(request):
    recommended_products = Product.objects.filter(is_active=True).order_by('?')
    categories = Category.objects.all()


    # Price filter values
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Default values if not provided
    if not min_price:
        min_price = 100
    if not max_price:
        max_price = 500000

    # Apply filter
    recommended_products = recommended_products.filter(
        price__gte=min_price,
        price__lte=max_price
    )


    paginator = Paginator(recommended_products, 8)  # 8 products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    return render(request, 'bestdeals.html', {
        'recommended_products': page_obj,
        'categories': categories,
        'page_obj' : page_obj,


    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, "product_detail.html", {"product": product})
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # Base product list for category
    products = Product.objects.filter(category=category, is_active=True)

    # Price filter values
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Default values if not provided
    if not min_price:
        min_price = 100
    if not max_price:
        max_price = 500000

    # Apply filter
    products = products.filter(
        price__gte=min_price,
        price__lte=max_price
    )

    paginator = Paginator(products, 8)  # 8 products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'category.html', {
        'category': category,
        'products': page_obj,
        'categories': Category.objects.all(),
        'page_obj': page_obj
    })
