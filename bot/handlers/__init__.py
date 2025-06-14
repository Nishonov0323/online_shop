# Bot handlers
from .start import get_start_router
from .categories import get_categories_router
from .products import get_products_router
from .cart import get_cart_router
from .orders import get_orders_router
from .contact import get_contact_router
from .settings import get_settings_router

__all__ = [
    'get_start_router',
    'get_categories_router',
    'get_products_router',
    'get_cart_router',
    'get_orders_router',
    'get_contact_router',
    'get_settings_router'
]