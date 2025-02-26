import csv, io
from django.http import Http404
from django.db import transaction
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from productos.models import Categoria, Detalles, PrecioDistribuidor

@staff_member_required
def update_db_view(request):
    page_name = 'apps/registros/productos/update.html'
    
    # Initial context
    context = {'msg': 'Lista cargada exitosamente'}

    # Handle GET request
    if request.method == 'GET':
        context['msg'] = 'Solo Archivos *.CSV'
        return render(request, page_name, context)

    # Check if a file was uploaded
    if 'file' not in request.FILES:
        context['msg'] = 'No se ha proporcionado ningún archivo.'
        return render(request, page_name, context)

    csv_file = request.FILES['file']

    # Validate file extension
    if not csv_file.name.endswith('.csv'):
        context['msg'] = 'Formato de Archivo NO VALIDO. Solo se permiten archivos *.CSV.'
        return render(request, page_name, context)

    try:
        # Decode and read the CSV file
        decoded_file = io.TextIOWrapper(csv_file.file, encoding='utf-8')
        reader = csv.DictReader(decoded_file)

        # Process each row in the CSV
        with transaction.atomic():
            for row in reader:
                # Validate required fields
                required_fields = ['categoria', 'distribuidor', 'consultor_mayor', 'productor_calificado',
                                   'mayorista']
                if not all(field in row for field in required_fields):
                    raise ValueError(f"Faltan campos obligatorios en el archivo CSV: {required_fields}")

                # Update or create the Categoria record
                precio_ds = PrecioDistribuidor.objects.create(
                    categoria = Categoria.objects.filter(nombre=str(row['categoria']), activo=True).first(),
                    distribuidor = float(row['distribuidor']),
                    consultor_mayor = float(row['consultor_mayor']),
                    productor_calificado = float(row['productor_calificado']),
                    mayorista = float(row['mayorista'])
                )
                precio_ds.save()
 

    except Exception as e:
        # Handle any errors during processing
        context['msg'] = f"Error al procesar el archivo: {str(e)}"
        return render(request, page_name, context)

    # Success message
    context['msg'] = 'Archivo procesado exitosamente.'
    return render(request, page_name, context)

def hx_sabores_categoria(request, id_categoria=None, id=None):
    if not request.htmx:
        raise Http404
    
    context, template = {}, 'apps/registros/productos/partials/sabores.html'
    id_categoria = request.GET.get('categoria')
    obj_list = Detalles.objects.filter(categoria=id_categoria)
    context['obj_list'] = obj_list
    return render(request, template, context)
