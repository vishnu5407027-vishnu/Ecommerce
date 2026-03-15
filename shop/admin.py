from django.contrib import admin
from .models import Category,Product,ProductImage
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4   # show 4 image upload slots


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "stock", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    inlines = [ProductImageInline]