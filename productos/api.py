from unicodedata import category
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CategoriaSerializer, PreciosDistribuidorSerializer
from .models import Categoria, PrecioDistribuidor


@api_view(['GET'])
def app_over_view(request):
    api_urls = {
        'list': '/api-list/',
        'detail view': '/api-detail/<str:pk>/',
        '': ''
    }

    return Response(api_urls)

@api_view(['GET'])
def search_products(request):
    search = request.GET.get('search')
    products_list = ''
    if search:
        products_list = Categoria.objects.filter(nombre__icontains=search)
    serializer = CategoriaSerializer(products_list, many=True)
    # print(serializer.data)
    return Response(serializer.data)

@api_view(['GET'])
def products_list(request):
    products = Categoria.objects.all()
    serializer = CategoriaSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def precios_dist_list(request):
    precios = PrecioDistribuidor.objects.all()
    serializer = PreciosDistribuidorSerializer(precios, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def product_detail(request, pk):
    product = Categoria.objects.get(id=pk)
    precios = PrecioDistribuidor.objects.filter(categoria=product, activo=True).first()
    serializer_p = PreciosDistribuidorSerializer(precios, many=False)
    serializer = CategoriaSerializer(product, many=False)
    
    return Response({'producto' : serializer.data, 'precios' : serializer_p.data})


@api_view(['POST'])
def product_create(request):
    serializer = CategoriaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(['POST'])
def product_update_or_create(request, pk):
    product, created = Categoria.objects.update_or_create(
        id = pk,
        defaults = {
            'nombre':request.data['nombre'],
            'descripcion': request.data['descripcion'],
            'cantidad': request.data['cantidad'],
            'puntos_volumen': request.data['puntos_volumen'],
            'distribuidor': request.data['distribuidor'],
            'consultor_mayor': request.data['consultor_mayor'],
            'productor_calificado': request.data['productor_calificado'],
            'mayorista': request.data['mayorista'],
            'cliente_bs': request.data['cliente_bs'],
            'cliente_sus': request.data['cliente_sus'],
            'activo': request.data['activo']
        }
    )
    
    serializer = CategoriaSerializer(product, many=False)
    # if serializer.is_valid():
    #     serializer.save()

    return Response(serializer.data)