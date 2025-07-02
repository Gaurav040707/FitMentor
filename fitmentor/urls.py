"""
URL configuration for fitmentor project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path,include
from backoffice_engine import views
from django.contrib.auth import views as auth_views
from backoffice_engine import views as app_views  
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.index),
    path('login/', views.login, name='login'),
    path('bmi/', views.bmi_calculator_view, name='bmi'),
    path("chatbot/", views.chat_view, name="chatbot"),
    path('about/',views.about),
    path('gallery/',views.gallery),
    path('contact/',views.contact),
    path('register/',views.register),
    path('forgot/',views.forgot),
    path('sendotp/',views.sendotp),
    path('reset/',views.reset),
    path('profile/', views.profile, name='profile'),
    path('logout/',views.logout),
    path('update/<int:id>', views.update_profile, name='update'),
    path('delete_account/<int:id>',views.delete_account),
    path('feedback/',views.feedback),
    path('chatbot/<int:conversation_id>/', views.chat_view, name='chatbot_conv'),
    path('chatbot/delete/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('chatbot/new/', views.new_chat, name='new_chat'),
    
]