from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/api/subscriptions/', permanent=False)),
    path('admin/', admin.site.urls),

    path('api/users/', include('users.urls')),

    path('api/subscriptions/', include('subscriptions.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
