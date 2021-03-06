"""tk_docker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.UserLogin, name='login'),
    url(r'^dashboard/$', views.Dashboard, name='dashboard'),
    url(r'^logout/$', views.UserLogout, name='logout'),
    url(r'^computer/$', views.Computer, name='computer'),
    url(r'^service_status/$', views.service_status, name='service_status'),
    url(r'^service_status_detection/$', views.service_status_detection, name='service_status_detection'),
]
