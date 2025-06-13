import pytest
from django.test import TestCase
from decimal import Decimal
from store.models import User, Category, Product, Color, Cart, CartItem, Order, OrderItem


class TestUser(TestCase):
    """Test User model"""

    def setUp(self):
        self.user = User.objects.create(
            telegram_id=123456789,
            first_name="Test User",
            phone_number="+998901234567",
            language="uz"
        )

    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(self.user.telegram_id, 123456789)
        self.assertEqual(self.user.first_name, "Test User")
        self.assertEqual(self.user.phone_number, "+998901234567")
        self.assertEqual(self.user.language, "uz")
        self.assertTrue(self.user.is_active)

    def test_user_str(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), f"Test User (123456789)")


class TestCategory(TestCase):
    """Test Category model"""

    def setUp(self):
        # Create parent category
        self.parent_category = Category.objects.create(
            name_uz="Elektronika",
            name_ru="Электроника"
        )

        # Create child category
        self.child_category = Category.objects.create(
            name_uz="Telefonlar",
            name_ru="Телефоны",
            parent=self.parent_category
        )

    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.parent_category.name_uz, "Elektronika")
        self.assertEqual(self.parent_category.name_ru, "Электроника")
        self.assertIsNone(self.parent_category.parent)

        self.assertEqual(self.child_category.name_uz, "Telefonlar")
        self.assertEqual(self.child_category.name_ru, "Телефоны")
        self.assertEqual(self.child_category.parent, self.parent_category)

    def test_category_str(self):
        """Test category string representation"""
        self.assertEqual(str(self.parent_category), "Elektronika")
        self.assertEqual(str(self.child_category), "Telefonlar")

    def test_get_name_method(self):
        """Test get_name method"""
        self.assertEqual(self.parent_category.get_name("uz"), "Elektronika")
        self.assertEqual(self.parent_category.get_name("ru"), "Электроника")

        self.assertEqual(self.child_category.get_name("uz"), "Telefonlar")
        self.assertEqual(self.child_category.get_name("ru"), "Телефоны")


class TestProduct(TestCase):
    """Test Product model"""

    def setUp(self):
        # Create category
        self.category = Category.objects.create(
            name_uz="Elektronika",
            name_ru="Электроника"
        )

        # Create product
        self.product = Product.objects.create(
            name_uz="iPhone 14",
            name_ru="Айфон 14",
            description_uz="Apple kompaniyasi telefoni",
            description_ru="Телефон компании Apple"
        )

        # Add category to product
        self.product.categories.add(self.category)

    def test_product_creation(self):
        """Test product creation"""
        self.assertEqual(self.product.name_uz, "iPhone 14")
        self.assertEqual(self.product.name_ru, "Айфон 14")
        self.assertEqual(self.product.description_uz, "Apple kompaniyasi telefoni")
        self.assertEqual(self.product.description_ru, "Телефон компании Apple")
        self.assertTrue(self.product.is_active)

    def test_product_str(self):
        """Test product string representation"""
        self.assertEqual(str(self.product), "iPhone 14")

    def test_product_category_relationship(self):
        """Test product-category relationship"""
        self.assertEqual(self.product.categories.count(), 1)
        self.assertEqual(self.product.categories.first(), self.category)

    def test_get_name_and_description_methods(self):
        """Test get_name and get_description methods"""
        self.assertEqual(self.product.get_name("uz"), "iPhone 14")
        self.assertEqual(self.product.get_name("ru"), "Айфон 14")

        self.assertEqual(self.product.get_description("uz"), "Apple kompaniyasi telefoni")
        self.assertEqual(self.product.get_description("ru"), "Телефон компании Apple")


class TestColorAndColorImage(TestCase):
    """Test Color and ColorImage models"""

    def setUp(self):
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

    def test_color_creation(self):
        """Test color creation"""
        self.assertEqual(self.color.name_uz, "Qora")
        self.assertEqual(self.color.name_ru, "Черный")
        self.assertEqual(self.color.price, Decimal('1200000.00'))
        self.assertTrue(self.color.is_active)

    def test_color_str(self):
        """Test color string representation"""
        self.assertEqual(str(self.color), "iPhone 14 - Qora")

    def test_get_name_method(self):
        """Test get_name method"""
        self.assertEqual(self.color.get_name("uz"), "Qora")
        self.assertEqual(self.color.get_name("ru"), "Черный")


class TestCartAndCartItem(TestCase):
    """Test Cart and CartItem models"""

    def setUp(self):
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

    def test_cart_creation(self):
        """Test cart creation"""
        self.assertEqual(self.cart.user, self.user)
        self.assertTrue(self.cart.is_active)

    def test_cart_item_creation(self):
        """Test cart item creation"""
        self.assertEqual(self.cart_item.cart, self.cart)
        self.assertEqual(self.cart_item.color, self.color)
        self.assertEqual(self.cart_item.quantity, 2)

    def test_cart_str(self):
        """Test cart string representation"""
        self.assertEqual(str(self.cart), f"Savatcha #{self.cart.id} - {self.user}")

    def test_cart_item_str(self):
        """Test cart item string representation"""
        self.assertEqual(str(self.cart_item), "iPhone 14 (Qora) x 2")

    def test_get_price_method(self):
        """Test get_price method of cart item"""
        self.assertEqual(self.cart_item.get_price(), Decimal('2400000.00'))

    def test_get_total_price_method(self):
        """Test get_total_price method of cart"""
        self.assertEqual(self.cart.get_total_price(), Decimal('2400000.00'))

        # Add another item
        color2 = Color.objects.create(
            product=self.product,
            name_uz="Oq",
            name_ru="Белый",
            price=Decimal('1300000.00')
        )

        CartItem.objects.create(
            cart=self.cart,
            color=color2,
            quantity=1
        )

        # Recalculate total price
        self.assertEqual(self.cart.get_total_price(), Decimal('3700000.00'))


class TestOrderAndOrderItem(TestCase):
    """Test Order and OrderItem models"""

    def setUp(self):
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

    def test_order_creation(self):
        """Test order creation"""
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, "new")
        self.assertEqual(self.order.address, "Test Address, 123")
        self.assertEqual(self.order.total_price, Decimal('2500000.00'))

    def test_order_item_creation(self):
        """Test order item creation"""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product_name, "iPhone 14")
        self.assertEqual(self.order_item.color_name, "Qora")
        self.assertEqual(self.order_item.price, Decimal('1250000.00'))
        self.assertEqual(self.order_item.quantity, 2)

    def test_order_str(self):
        """Test order string representation"""
        self.assertEqual(str(self.order), f"Buyurtma #{self.order.id} - Test User")

    def test_order_item_str(self):
        """Test order item string representation"""
        self.assertEqual(str(self.order_item), "iPhone 14 (Qora) x 2")