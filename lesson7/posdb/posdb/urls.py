# posdb/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',          RedirectView.as_view(url='/accounts/login/'), name='home'),  # / → login page"
    path('admin/', admin.site.urls),          # /admin/  → ផ្ទាំង Django admin
    path('sales/', include('sales.urls')),    # /sales/  → បញ្ជូនទៅ sales/urls.py
    path('accounts/', include('django.contrib.auth.urls')), # login , logout, change password
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ឧទាហរណ៍លំហូរ URL:
# Request: GET /sales/products/3/
# ផ្គូផ្គង: path('sales/', ...) → កាត់ 'sales/' ហើយបញ្ជូន 'products/3/' ទៅ sales/urls.py
# ផ្គូផ្គង: path('products/<int:pk>/', ...) → ហៅ product_detail(request, pk=3)
# URL map:
# /                  → redirect to /accounts/login/
# /accounts/login/   → login page
# /accounts/logout/  → logs the user out
# /sales/products/   → product catalogue  (requires login)
# /sales/orders/     → orders list        (requires login)
# /admin/            → Django admin panel