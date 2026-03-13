 
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Dashboard
    path('', views.home, name='home'),

    # Medicines
    path('medicines/',                  views.medicine_list,   name='medicine_list'),
    path('medicines/add/',              views.medicine_add,    name='medicine_add'),
    path('medicines/<int:pk>/',         views.medicine_detail, name='medicine_detail'),
    path('medicines/<int:pk>/edit/',    views.medicine_edit,   name='medicine_edit'),
    path('medicines/<int:pk>/delete/',  views.medicine_delete, name='medicine_delete'),

    # Suppliers
    path('suppliers/',                  views.supplier_list,   name='supplier_list'),
    path('suppliers/add/',              views.supplier_add,    name='supplier_add'),
    path('suppliers/<int:pk>/edit/',    views.supplier_edit,   name='supplier_edit'),
    path('suppliers/<int:pk>/delete/',  views.supplier_delete, name='supplier_delete'),

    # Customers
    path('customers/',                  views.customer_list,   name='customer_list'),
    path('customers/add/',              views.customer_add,    name='customer_add'),
    path('customers/<int:pk>/edit/',    views.customer_edit,   name='customer_edit'),
    path('customers/<int:pk>/delete/',  views.customer_delete, name='customer_delete'),

    # Purchases
    path('purchases/',                  views.purchase_list,   name='purchase_list'),
    path('purchases/add/',              views.purchase_add,    name='purchase_add'),
    path('purchases/<int:pk>/edit/',    views.purchase_edit,   name='purchase_edit'),
    path('purchases/<int:pk>/delete/',  views.purchase_delete, name='purchase_delete'),

    # Sales
    path('sales/',                      views.sale_list,       name='sale_list'),
    path('sales/add/',                  views.sale_add,        name='sale_add'),
    path('sales/<int:pk>/edit/',        views.sale_edit,       name='sale_edit'),
    path('sales/<int:pk>/delete/',      views.sale_delete,     name='sale_delete'),

    # Contact
    path('contact/', views.contact, name='contact'),
]
