from django.urls import path
from . import views
app_name="shop"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.category_products, name="category_products"),
    path("best_deals", views.best_deals, name="best_deals"),

]
