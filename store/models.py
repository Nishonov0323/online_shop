from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    """User model for storing Telegram user data"""
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)  # Qo'shildi
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)  # Qo'shildi
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    language = models.CharField(max_length=5, choices=[('uz', 'Uzbek'), ('ru', 'Russian')], default='uz')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Foydalanuvchi")
        verbose_name_plural = _("Foydalanuvchilar")

    def __str__(self):
        return f"{self.first_name} ({self.telegram_id})"


class Category(models.Model):
    """Category model for product categories"""
    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Kategoriya")
        verbose_name_plural = _("Kategoriyalar")

    def __str__(self):
        return self.name_uz

    def get_name(self, language):
        """Get name based on language"""
        return getattr(self, f'name_{language}')


class Product(models.Model):
    """Product model"""
    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    description_uz = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='products')
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Mahsulot")
        verbose_name_plural = _("Mahsulotlar")

    def __str__(self):
        return self.name_uz

    def get_name(self, language):
        """Get name based on language"""
        return getattr(self, f'name_{language}')

    def get_description(self, language):
        """Get description based on language"""
        return getattr(self, f'description_{language}')


class Color(models.Model):
    """Color model (product variant)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    name_uz = models.CharField(max_length=50)
    name_ru = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Rang")
        verbose_name_plural = _("Ranglar")

    def __str__(self):
        return f"{self.product.name_uz} - {self.name_uz}"

    def get_name(self, language):
        """Get name based on language"""
        return getattr(self, f'name_{language}')


class ColorImage(models.Model):
    """Images for product colors"""
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_colors/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Rang rasmi")
        verbose_name_plural = _("Rang rasmlari")
        ordering = ['order']

    def __str__(self):
        return f"{self.color} - {self.id}"


class Cart(models.Model):
    """Cart model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Savatcha")
        verbose_name_plural = _("Savatchalar")

    def __str__(self):
        return f"Savatcha #{self.id} - {self.user}"

    def get_total_price(self):
        """Calculate total price of cart items"""
        return sum(item.get_price() for item in self.items.all())


class CartItem(models.Model):
    """Cart item model"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _("Savatcha elementi")
        verbose_name_plural = _("Savatcha elementlari")

    def __str__(self):
        return f"{self.color.product.name_uz} ({self.color.name_uz}) x {self.quantity}"

    def get_price(self):
        """Calculate price of cart item"""
        return self.color.price * self.quantity


class Order(models.Model):
    """Order model"""
    STATUS_CHOICES = [
        ('new', _('Yangi')),
        ('processing', _('Jarayonda')),
        ('shipped', _('Yuborilgan')),
        ('delivered', _('Yetkazilgan')),
        ('cancelled', _('Bekor qilingan')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    address = models.TextField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Buyurtma")
        verbose_name_plural = _("Buyurtmalar")

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.user.first_name}"


class OrderItem(models.Model):
    """Order item model"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    color_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _("Buyurtma elementi")
        verbose_name_plural = _("Buyurtma elementlari")

    def __str__(self):
        return f"{self.product_name} ({self.color_name}) x {self.quantity}"