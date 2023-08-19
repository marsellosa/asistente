from django.urls import path
from recetas.views import *

app_name = 'recetas'

urlpatterns = [
    path("", recipe_list_view, name='list'),
    path("create/", recipe_create_view, name='create'),
    path("search/", search_view, name='search'),
    path("hx/<int:parent_id>/ingrediente/<int:id>/", recipe_ingredient_update_hx_view, name='hx-ingredient-detail'),
    path("hx/<int:parent_id>/ingrediente-herbal/<int:id>/", recipe_herbal_ingredient_update_hx_view, name='hx-herbal-ingredient-detail'),
    path("hx/<int:parent_id>/ingrediente/", recipe_ingredient_update_hx_view, name='hx-ingredient-create'),
    path("hx/<int:parent_id>/ingrediente-herbal/", recipe_herbal_ingredient_update_hx_view, name='hx-herbal-ingredient-create'),
    path("hx/<int:id>/", recipe_detail_hx_view, name='hx-detail'),
    path("<int:parent_id>/ingrediente/<int:id>/delete/", recipe_ingredient_delete_view, name='ingredient-delete'),
    path("<int:parent_id>/ingrediente-herbal/<int:id>/delete/", recipe_herbal_ingredient_delete_view, name='herbal-ingredient-delete'),
    path("<int:id>/delete/", recipe_delete_view, name='delete'),
    path("<int:id>/edit/", recipe_update_view, name='update'),
    path("<int:id>/", recipe_detail_view, name='detail'),
    path("<int:id>/crud/", htmx_crud_recipe_view, name='crud'),
    
]
