from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import User, Category, Product, Color, ColorImage, Cart, CartItem, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'telegram_id', 'first_name', 'phone_number', 'language', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ColorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorImage
        fields = ['id', 'image', 'order']


class ColorSerializer(serializers.ModelSerializer):
    images = ColorImageSerializer(many=True, read_only=True)

    class Meta:
        model = Color
        fields = ['id', 'name_uz', 'name_ru', 'price', 'is_active', 'images']


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name_uz', 'name_ru', 'parent', 'image', 'is_active', 'children']

    @extend_schema_field(serializers.ListSerializer(child=serializers.DictField()))
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []


class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    colors = ColorSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name_uz', 'name_ru', 'description_uz', 'description_ru',
                  'categories', 'colors', 'main_image', 'is_active']


class CartItemSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    product = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'color', 'product', 'quantity', 'total_price']

    @extend_schema_field(serializers.DictField())
    def get_product(self, obj):
        """Get product information"""
        product = obj.color.product
        return {
            'id': product.id,
            'name_uz': product.name_uz,
            'name_ru': product.name_ru,
            'main_image': product.main_image.url if product.main_image else None
        }

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total_price(self, obj):
        """Calculate total price for this cart item"""
        return obj.get_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'is_active', 'items', 'total_price', 'items_count', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total_price(self, obj):
        """Calculate total price of all items in cart"""
        return obj.get_total_price()

    @extend_schema_field(serializers.IntegerField())
    def get_items_count(self, obj):
        """Get total number of items in cart"""
        return obj.items.count()


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'color_name', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'address', 'total_price', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


# Additional serializers for specific API operations
class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    color_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating order"""
    address = serializers.CharField(max_length=500)
