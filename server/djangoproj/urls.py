"""Routes for Django administration, API and React navigation."""
from django.contrib import admin
from django.urls import include, path, re_path
from djangoapp import views
urlpatterns = [path('admin/', admin.site.urls), path('djangoapp/', include('djangoapp.urls')),
    path('health/', views.health), path('about/', views.about), path('contact/', views.contact),
    re_path(r'^(?:|login|register|dealer/\d+|postreview/\d+)/?$', views.frontend)]
