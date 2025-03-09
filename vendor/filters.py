import django_filters
from  product.models import Product



class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category__title", lookup_expr="icontains")
    in_stock = django_filters.BooleanFilter(field_name="in_stock")
    
    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price", "in_stock"]