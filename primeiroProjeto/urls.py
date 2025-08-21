from django.urls import path
from Connect_Sync import views
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('admin/', admin.site.urls),

]
