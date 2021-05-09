from django.urls import path

from snaver import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('', views.index, name='logout'),

]
