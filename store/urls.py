from django.urls import path
from . import views

urlpatterns = [
    path('',views.store,name='store'),
    path('product/<str:pk>',views.detail,name='detail'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('update-item/',views.updateItem, name='update-item'),
    path('process-order/',views.processOrder, name='process-order')
]