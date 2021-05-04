from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('api/v1/', include('pollsAPI.urls')),
    path('docs/', include_docs_urls(title='Polls API')),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
]
