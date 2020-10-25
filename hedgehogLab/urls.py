"""hedgehogLab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

import PostsApp.views as views

schema_view = get_schema_view(
   openapi.Info(
      title="Hedgehog Lab Test API",
      default_version='v1',
      description="API documentation",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^doc/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^doc/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^doc/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^api/v1/users/$', views.UserListAPI.as_view(), name='user-api-v1'),
    re_path(r'^api/v1/posts/$', views.PostListAPI.as_view(), name='post-api-v1'),
    re_path(r'^api/v1/images/$', views.ImageListAPI.as_view(), name='image-api-v1'),
    re_path(r'^api/v1/likepost/$', views.PostLikeAPI.as_view(), name='post-like-api-v1'),
    re_path(r'^api/v1/followuser/$', views.UserFollowAPI.as_view(), name='user-follow-api-v1'),
]
