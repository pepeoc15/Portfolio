"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
    path("auth/", include("apps.p_auth.urls")),
    path(
        ".well-known/appspecific/com.chrome.devtools.json",
        lambda request: HttpResponse(status=204),
    ),
    path("admin/", admin.site.urls),
    path("dgt-acc-viz/", include("apps.dgt_acc_viz.urls")),
    path("moc-beauty/", include("apps.moc_beauty.urls")),
    path("", include("apps.portfolio.urls")),
]