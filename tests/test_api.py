import json
from decimal import Decimal
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Category, Product, Color, Cart, CartItem, Order, OrderItem


class TestUserAPI(TestCase):
    """Test User API"""

    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create(
            telegram_id=123456789,
            first_name="User One",
            phone_number="+998901234567",
            language="uz"
        )

        self.user2 = User.objects.create(
            telegram_id=987654321,
            first_name="User Two",
            phone_number="+998907654321",
            language="ru",
            is_active=False
        )

    def test_get_user_list(self):
        """Test getting user list"""
        url = reverse('user-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_user_detail(self):
        """Test getting user detail"""
        url = reverse('user-detail', args=[self.user1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['telegram_id'], self.user1.telegram_id)
        self.assertEqual(response.data['first_name'], self.user1.first_name)
        self.assertEqual(response.data['phone_number'], self.user1.phone_number)

    def test_toggle_user_active(self):
        """Test toggling user active status"""
        url = reverse('user-toggle-active', args=[self.user1.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], False)

        # Refresh from DB
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_active)


class TestCategoryAPI(TestCase):
    """Test Category API"""

    def setUp(self):
        self.client = APIClient()

        # Create test categories
        self.parent_category = Category.objects.create(
            name_uz="Elektronika",
            name_ru="Электроника"
        )

        self.child_category1 = Category.objects.create(
            name_uz="Telefonlar",
            name_ru="Телефоны",
            parent=self.parent_category
        )

        self.child_category2 = Category.objects.create(
            name_uz="Noutbuklar",
            name_ru="Ноутбуки",
            parent=self.parent_category
        )

    def test_get_category_list(self):
        """Test getting category list"""
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only parent category

    def test_get_category_with_parent_filter(self):
        """Test getting categories with parent filter"""
        url = f"{reverse('category-list')}?parent={self.parent_category.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Two child categories

    def test_get_category_detail(self):
        """Test getting category detail with children"""
        url = reverse('category-detail', args=[self.parent_category.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name_uz'], self.parent_category.name_uz)
        self.assertEqual(len(response.data['children']), 2)  # Two child categories


class TestProductAPI(TestCase):
    """Test Product API"""

    def setUp(self):
        self.client = APIClient()

        # Create test category
        self.category = Category.objects.create(
            name_uz="Elektronika",
            name_ru="Электроника"
        )

        # Create test products
        self.product1 = Product.objects.create(
            name_uz="iPhone 14",
            name_ru="Айфон 14",
            description_uz="Apple kompaniyasi telefoni",
            description_ru="Телефон компании Apple"
        )
        self.product1.categories.add(self.category)

        self.product2 = Product.objects.create(
            name_uz="Samsung Galaxy S20",
            name_ru="Самсунг Галакси S20"
        )
        self.product2.categories.add(self.category)

        # Create colors for products
        self.color1 = Color.objects.create(
            product=self.product1,
            name_uz="Qora",
            name_ru="Черный",
            price=Decimal('1200000.00')
        )

        self.color2 = Color.objects.create(
            product=self.product1,
            name_uz="Oq",
            name_ru="Белый",
            price=Decimal('1250000.00')
        )

    def test_get_product_list(self):
        """Test getting product list"""
        url = reverse('product-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_products_by_category(self):
        """Test getting products filtered by category"""
        url = f"{reverse('product-list')}?categories={self.category.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_product_detail(self):
        """Test getting product detail with colors"""
        url = reverse('product-detail', args=[self.product1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name_uz'], self.product1.name_uz)
        self.assertEqual(len(response.data['colors']), 2)


class TestCartAPI(TestCase):
    """Test Cart API"""

    def setUp(self):
        self.client = APIClient()

        # Create user
        self.user = User.objects.create(
            telegram_id=123456789,
            first_name="Test User"
        )

        # Create product
        self.product = Product.objects.create(
            name_uz="iPhone 14",
            name_ru="Айфон 14"
        )

        # Create color
        self.color = Color.objects.create(
            product=self.product,
            name_uz="Qora",
            name_ru="Черный",
            price=Decimal('1200000.00')
        )

        # Create cart
        self.cart = Cart.objects.create(
            user=self.user,
            is_active=True
        )

        # Create cart item
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            color=self.color,
            quantity=2
        )

    def test_get_cart_list(self):
        """Test getting cart list"""
        url = reverse('cart-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_cart_by_user(self):
        """Test getting cart filtered by user"""
        url = f"{reverse('cart-list')}?user={self.user.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.user.id)

    def test_get_cart_detail(self):
        """Test getting cart detail with items"""
        url = reverse('cart-detail', args=[self.cart.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['total_price'], '2400000.00')


class TestOrderAPI(TestCase):
    """Test Order API"""

    def setUp(self):
        self.client = APIClient()

        # Create user
        self.user = User.objects.create(
            telegram_id=123456789,
            first_name="Test User"
        )

        # Create order
        self.order = Order.objects.create(
            user=self.user,
            status="new",
            address="Test Address, 123",
            total_price=Decimal('2500000.00')
        )

        # Create order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product_name="iPhone 14",
            color_name="Qora",
            price=Decimal('1250000.00'),
            quantity=2
        )

    def test_get_order_list(self):
        """Test getting order list"""
        url = reverse('order-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_order_by_user(self):
        """Test getting order filtered by user"""
        url = f"{reverse('order-list')}?user={self.user.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.user.id)

    def test_get_order_detail(self):
        """Test getting order detail with items"""
        url = reverse('order-detail', args=[self.order.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['status'], 'new')
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['total_price'], '2500000.00')

    def test_change_order_status(self):
        """Test changing order status"""
        url = reverse('order-change-status', args=[self.order.id])
        response = self.client.post(url, {'status': 'processing'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_status'], 'processing')

        # Refresh from DB
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'processing')