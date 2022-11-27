from dataclasses import fields
from rest_framework.serializers import ModelSerializer
from productos.models import Categoria, PrecioDistribuidor

class CategoriaSerializer(ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class PreciosDistribuidorSerializer(ModelSerializer):
    class Meta:
        model = PrecioDistribuidor
        fields = '__all__'