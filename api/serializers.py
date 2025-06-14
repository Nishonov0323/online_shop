from rest_framework import serializers
from store.models import User, Category, Product, Color, Cart, CartItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []


class ProductSerializer(serializers.ModelSerializer):
    colors = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_colors(self, obj):
        return ColorSerializer(obj.colors.filter(is_active=True), many=True).data


class ColorSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Color
        fields = '__all__'

    def get_images(self, obj):
        return [img.image.url for img in obj.images.all()]