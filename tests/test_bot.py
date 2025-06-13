from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.handlers.cart import show_cart, remove_from_cart
from bot.handlers.categories import show_categories, process_category
from bot.handlers.products import process_product, process_add_to_cart
from bot.handlers.start import start_cmd, language_selection, name_input, phone_handler_contact
from store.models import User, Cart


class TestStartHandlers:
    """Test start.py handlers"""

    @pytest.mark.asyncio
    async def test_start_cmd_new_user(self):
        """Test start command for new user"""
        # Mock objects
        message = AsyncMock(spec=types.Message)
        message.from_user.id = 123456789
        message.chat.id = 123456789

        state = AsyncMock(spec=FSMContext)

        # Mock User.objects.get to raise DoesNotExist
        with patch('store.models.User.objects.get', side_effect=User.DoesNotExist):
            await start_cmd(message, state)

        # Check behavior
        state.clear.assert_called_once()
        message.answer.assert_called_once()
        args, kwargs = message.answer.call_args
        assert "Tilni tanlang" in args[0]

    @pytest.mark.asyncio
    async def test_start_cmd_existing_user(self):
        """Test start command for existing user"""
        # Mock objects
        message = AsyncMock(spec=types.Message)
        message.from_user.id = 123456789
        message.chat.id = 123456789

        state = AsyncMock(spec=FSMContext)

        # Mock user
        mock_user = MagicMock()
        mock_user.first_name = "Test User"
        mock_user.language = "uz"

        # Mock User.objects.get to return user
        with patch('store.models.User.objects.get', return_value=mock_user):
            await start_cmd(message, state)

        # Check behavior
        state.clear.assert_called_once()
        message.answer.assert_called_once()
        args, kwargs = message.answer.call_args
        assert "Xush kelibsiz" in args[0]

    @pytest.mark.asyncio
    async def test_language_selection_valid(self):
        """Test language selection with valid input"""
        # Mock objects
        message = AsyncMock(spec=types.Message)
        message.text = "🇺🇿 O'zbekcha"

        state = AsyncMock(spec=FSMContext)

        await language_selection(message, state)

        # Check behavior
        state.update_data.assert_called_once_with(language="uz")
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_language_selection_invalid(self):
        """Test language selection with invalid input"""
        # Mock objects
        message = AsyncMock(spec=types.Message)
        message.text = "Invalid"

        state = AsyncMock(spec=FSMContext)

        await language_selection(message, state)

        # Check behavior
        state.update_data.assert_not_called()
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_name_input_valid(self):
        """Test name input with valid name"""
        # Mock objects
        message = AsyncMock(spec=types.Message)
        message.text = "John Doe"

        state = AsyncMock(spec=FSMContext)
        state.get_data.return_value = {"language": "uz"}

        await name_input(message, state)

        # Check behavior
        state.update_data.assert_called_once_with(first_name="John Doe")
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_name_input_invalid(self):
        """Test name input with invalid name"""
        # Mock objects
        message = AsyncMock(spec=types.Message)
        message.text = "A"  # Too short

        state = AsyncMock(spec=FSMContext)
        state.get_data.return_value = {"language": "uz"}

        await name_input(message, state)

        # Check behavior
        state.update_data.assert_not_called()
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_phone_handler_contact(self):
        """Test phone handler with contact"""
        # Mock objects
        message = AsyncMock(spec=types.Message)
        message.contact.phone_number = "+998901234567"

        state = AsyncMock(spec=FSMContext)
        state.get_data.return_value = {
            "language": "uz",
            "first_name": "John Doe"
        }

        # Mock User.objects.create
        with patch('store.models.User.objects.create') as mock_create:
            await phone_handler_contact(message, state)

        # Check behavior
        mock_create.assert_called_once()
        state.clear.assert_called_once()
        message.answer.assert_called_once()


class TestCategoryHandlers:
    """Test categories.py handlers"""

    @pytest.mark.asyncio
    async def test_show_categories_with_categories(self):
        """Test show_categories with existing categories"""
        # Mock objects
        message = AsyncMock(spec=types.Message)

        user = MagicMock()
        user.language = "uz"

        # Mock categories
        categories = [MagicMock(), MagicMock()]

        # Mock Category.objects.filter
        with patch('store.models.Category.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = True
            mock_filter.return_value.__iter__.return_value = categories

            await show_categories(message, user)

        # Check behavior
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_categories_no_categories(self):
        """Test show_categories with no categories"""
        # Mock objects
        message = AsyncMock(spec=types.Message)

        user = MagicMock()
        user.language = "uz"

        # Mock Category.objects.filter
        with patch('store.models.Category.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False

            await show_categories(message, user)

        # Check behavior
        message.answer.assert_called_once()
        args, kwargs = message.answer.call_args
        assert "mavjud emas" in args[0]

    @pytest.mark.asyncio
    async def test_process_category_with_subcategories(self):
        """Test process_category with subcategories"""
        # Mock objects
        callback = AsyncMock(spec=types.CallbackQuery)
        callback.data = "category_1"

        user = MagicMock()
        user.language = "uz"

        # Mock category
        category = MagicMock()
        category.id = 1
        category.get_name.return_value = "Test Category"

        # Mock subcategories
        subcategories = [MagicMock(), MagicMock()]

        # Mock Category.objects.get and subcategories
        with patch('store.models.Category.objects.get', return_value=category), \
                patch.object(category.children, 'filter') as mock_filter:
            mock_filter.return_value.exists.return_value = True
            mock_filter.return_value.__iter__.return_value = subcategories

            await process_category(callback, user)

        # Check behavior
        callback.message.edit_text.assert_called_once()
        callback.answer.assert_called_once()


class TestProductHandlers:
    """Test products.py handlers"""

    @pytest.mark.asyncio
    async def test_process_product(self):
        """Test process_product handler"""
        # Mock objects
        callback = AsyncMock(spec=types.CallbackQuery)
        callback.data = "product_1"

        user = MagicMock()
        user.language = "uz"

        # Mock product
        product = MagicMock()
        product.get_name.return_value = "Test Product"
        product.get_description.return_value = "Test Description"
        product.main_image = None

        # Mock Product.objects.get
        with patch('store.models.Product.objects.get', return_value=product):
            await process_product(callback, user)

        # Check behavior
        callback.message.edit_text.assert_called_once()
        callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_add_to_cart(self):
        """Test process_add_to_cart handler"""
        # Mock objects
        callback = AsyncMock(spec=types.CallbackQuery)
        callback.data = "add_to_cart_1_1"

        user = MagicMock()

        # Mock color and cart
        color = MagicMock()
        cart = MagicMock()
        cart_item = MagicMock()

        # Mock Color.objects.get and Cart operations
        with patch('store.models.Color.objects.get', return_value=color), \
                patch('store.models.Cart.objects.get_or_create', return_value=(cart, True)), \
                patch('store.models.CartItem.objects.get_or_create', return_value=(cart_item, True)):
            await process_add_to_cart(callback, user)

        # Check behavior
        callback.answer.assert_called_once()


class TestCartHandlers:
    """Test cart.py handlers"""

    @pytest.mark.asyncio
    async def test_show_cart_with_items(self):
        """Test show_cart with items in cart"""
        # Mock objects
        message = AsyncMock(spec=types.Message)

        user = MagicMock()
        user.language = "uz"

        # Mock cart and items
        cart = MagicMock()
        cart_items = [MagicMock(), MagicMock()]
        cart.items.all.return_value = cart_items

        # Mock Cart.objects.get
        with patch('store.models.Cart.objects.get', return_value=cart):
            await show_cart(message, user)

        # Check behavior
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_cart_empty(self):
        """Test show_cart with empty cart"""
        # Mock objects
        message = AsyncMock(spec=types.Message)

        user = MagicMock()
        user.language = "uz"

        # Mock Cart.objects.get to raise DoesNotExist
        with patch('store.models.Cart.objects.get', side_effect=Cart.DoesNotExist):
            await show_cart(message, user)

        # Check behavior
        message.answer.assert_called_once()
        args, kwargs = message.answer.call_args
        assert "bo'sh" in args[0]

    @pytest.mark.asyncio
    async def test_remove_from_cart(self):
        """Test remove_from_cart handler"""
        # Mock objects
        callback = AsyncMock(spec=types.CallbackQuery)
        callback.data = "remove_1"

        user = MagicMock()
        user.language = "uz"

        # Mock cart item and cart
        cart_item = MagicMock()
        cart = MagicMock()
        cart.items.exists.return_value = True

        # Mock CartItem.objects.get and related operations
        with patch('store.models.CartItem.objects.get', return_value=cart_item), \
                patch('store.models.Cart.objects.get', return_value=cart):
            await remove_from_cart(callback, user)

        # Check behavior
        cart_item.delete.assert_called_once()
        callback.answer.assert_called_once()
        callback.message.delete.assert_called_once()
        callback.message.answer.assert_called_once()