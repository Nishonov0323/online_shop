from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.shortcuts import render
from django.http import JsonResponse


def home_view(request):
    """Bosh sahifa ko'rinishi"""
    context = {
        'title': 'Online Shop',
        'description': 'Python Django da yaratilgan zamonaviy online do\'kon API',
        'features': [
            'REST API with ViewSets',
            'Spectacular/Swagger dokumentatsiya',
            'Redoc dokumentatsiya',
            'Admin Panel',
            'Foydalanuvchi boshqaruvi',
            'Mahsulotlar katalogi',
            'Buyurtmalar tizimi',
            'Savatcha funksiyasi',
            'Kategoriyalar',
            'Ranglar va rasmlar'
        ],
        'endpoints': {
            'api': '/api/',
            'admin': '/admin/',
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
            'schema': '/api/schema/'
        }
    }
    return render(request, 'home.html', context)


def api_info(request):
    """API haqida ma'lumot"""
    return JsonResponse({
        'message': 'Online Shop API',
        'version': 'v1.0.0',
        'author': 'Nishonov0323',
        'framework': 'Django REST Framework',
        'documentation': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
            'schema': '/api/schema/',
        },
        'endpoints': {
            'users': '/api/users/',
            'categories': '/api/categories/',
            'products': '/api/products/',
            'colors': '/api/colors/',
            'color_images': '/api/color-images/',
            'carts': '/api/carts/',
            'orders': '/api/orders/',
        },
        'admin_panel': '/admin/',
        'github': 'https://github.com/Nishonov0323/online_shop',
        'total_endpoints': 7,
        'api_features': [
            'CRUD operations',
            'Filtering and Search',
            'Pagination',
            'Authentication',
            'Permissions',
            'Validation'
        ]
    })


urlpatterns = [
    # Bosh sahifa
    path('', home_view, name='home'),

    # Admin panel
    path('admin/', admin.site.urls),

    # API yo'nalishlari
    path('api/', include('api.urls')),
    path('api/info/', api_info, name='api-info'),

    # API dokumentatsiya - Spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-alt'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-alt'),
]

# Add media and static urls in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar (agar o'rnatilgan bo'lsa)
    try:
        import debug_toolbar

        urlpatterns = [
                          path('__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns
    except ImportError:
        pass

# Admin panel konfiguratsiyasi
admin.site.site_header = "Online Shop Admin"
admin.site.site_title = "Online Shop Admin Portal"
admin.site.index_title = "Online Shop Admin Panel"