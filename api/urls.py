from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views
from django.http import JsonResponse

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'colors', views.ColorViewSet)
router.register(r'color-images', views.ColorImageViewSet)
router.register(r'carts', views.CartViewSet)
router.register(r'orders', views.OrderViewSet)

def api_root_info(request):
    """API asosiy ma'lumotlari"""
    return JsonResponse({
        'message': 'Online Shop REST API',
        'version': 'v1.0.0',
        'endpoints': {
            'users': request.build_absolute_uri('users/'),
            'categories': request.build_absolute_uri('categories/'),
            'products': request.build_absolute_uri('products/'),
            'colors': request.build_absolute_uri('colors/'),
            'color_images': request.build_absolute_uri('color-images/'),
            'carts': request.build_absolute_uri('carts/'),
            'orders': request.build_absolute_uri('orders/'),
        },
        'documentation': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
            'schema': '/api/schema/',
        },
        'browsable_api': True,
        'authentication': ['SessionAuthentication', 'TokenAuthentication'],
        'permissions': ['IsAuthenticatedOrReadOnly'],
    })

urlpatterns = [
    path('', api_root_info, name='api-root-info'),
    path('v1/', include(router.urls)),
] + router.urls