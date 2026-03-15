from django.shortcuts import render
from shop.models import Product
from django.db.models import Q

def product_search(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )

    return render(request, 'search.html', {
        'query': query,
        'results': results
    })
