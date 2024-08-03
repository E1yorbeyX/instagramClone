from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title='Instagram_Clone',
        default_version="v1",
        description="Bu API da biz instagarmning authentication va boshqa bazi funksiyalarini yozib chiqdik marhamat tekinga ishlatishingiz mumkin",
        contact=openapi.Contact(email="xe1yorbey@gmail.com"),
        licence=openapi.License(name="E1yorbeyX")
    ),
    public=True,
    permission_classes = [permissions.AllowAny, ]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('posts/', include('posts.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc')
]
