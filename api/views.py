from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from store.models import (
    Category, Product, Color, ColorImage, User,
    Cart, CartItem, Order, OrderItem
)
from store.serializers import (
    CategorySerializer, ProductSerializer, ColorSerializer, ColorImageSerializer,
    UserSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['first_name', 'phone_number', 'telegram_id']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Foydalanuvchini faollashtirish/bloklash"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'status': 'success', 'is_active': user.is_active})


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name_uz', 'name_ru']

    def get_queryset(self):
        # Faqat asosiy (parent=None) kategoriyalarni qaytaradi
        if self.action == 'list' and not self.request.query_params.get('parent'):
            return Category.objects.filter(parent=None)
        return super().get_queryset()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categories', 'is_active']
    search_fields = ['name_uz', 'name_ru', 'description_uz', 'description_ru']


class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'is_active']


class ColorImageViewSet(viewsets.ModelViewSet):
    queryset = ColorImage.objects.all()
    serializer_class = ColorImageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['color']


class CartViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cart.objects.filter(is_active=True)
    serializer_class = CartSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'status']
    search_fields = ['id']

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Buyurtma statusini o'zgartirish"""
        order = self.get_object()
        status = request.data.get('status')

        if status not in dict(Order.ORDER_STATUS).keys():
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = status
        order.save()
        return Response({'status': 'success', 'order_status': order.status})