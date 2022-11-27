import csv, io
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from productos.models import Categoria, Detalles

@staff_member_required
def update_db_view(request):
    page_name = 'apps/registros/productos/update.html'
    context = {
        'msg':'Lista cargada exitosamente'
    }

    if request.method == 'GET':
        return render(request, page_name, {'msg':'Solo Archivos *.CSV'})

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        return render(request, page_name, {'msg':'Formato de Archivo NO VALIDO'})
        
    file = io.TextIOWrapper(csv_file)
    productos = csv.DictReader(file)

    for producto in productos:
        Categoria.objects.update_or_create(
            nombre = str(producto['nombre']),
            defaults={
                'descripcion' : str(producto['descripcion']),
                'cantidad' : int(producto['cantidad']),
                'puntos_volumen' : float(producto['puntos_volumen']),
                'distribuidor' : float(producto['distribuidor']),
                'consultor_mayor' : float(producto['consultor_mayor']),
                'productor_calificado' : float(producto['productor_calificado']),
                'mayorista' : float(producto['mayorista']),
                'cliente_bs' : float(producto['cliente_bs']),
                'cliente_sus' : float(producto['cliente_sus'])
            }
        )

    return render(request, page_name, context)

def hx_sabores_categoria(request, id_categoria=None, id=None):
    context, template = {}, 'apps/registros/productos/partials/sabores.html'
    id_categoria = request.GET.get('categoria')
    obj_list = Detalles.objects.filter(categoria=id_categoria)
    context['obj_list'] = obj_list
    return render(request, template, context)
