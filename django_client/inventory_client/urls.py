from django.urls import path
from . import views

app_name = "inventory_client"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("producto/<str:prod_id>/", views.product_detail, name="product_detail"),
    path("crear/", views.product_create, name="product_create"),
    path("editar/<str:prod_id>/", views.product_edit, name="product_edit"),
    path("eliminar/<str:prod_id>/", views.product_delete, name="product_delete"),
]
