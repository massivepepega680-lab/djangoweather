from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('', RedirectView.as_view(url='/api/subscriptions/', permanent=False)),
    path('admin/', admin.site.urls),

    path('api/users/register/', include('users.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),

    path('api/users/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api-auth/', include('rest_framework.urls')),
]
