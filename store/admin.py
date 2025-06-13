from django.contrib import admin
from .models import User, Category, Product, Color, ColorImage, Cart, CartItem, Order, OrderItem

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'first_name', 'phone_number', 'language', 'is_active')
    list_filter = ('language', 'is_active')
    search_fields = ('telegram_id', 'first_name', 'phone_number')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'parent', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name_uz', 'name_ru')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'is_active')
    list_filter = ('is_active', 'categories')
    search_fields = ('name_uz', 'name_ru')
    filter_horizontal = ('categories',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'name_uz', 'name_ru', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name_uz', 'name_ru', 'product__name_uz')

@admin.register(ColorImage)
class ColorImageAdmin(admin.ModelAdmin):
    # 'order' o'rniga 'image' ishlatilmoqda
    list_display = ('color', 'image')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at')
    list_filter = ('is_active',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'color', 'quantity')
    list_filter = ('cart__is_active',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_price', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__first_name', 'address')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'color_name', 'price', 'quantity')
    list_filter = ('order__status',)
    search_fields = ('product_name', 'color_name')