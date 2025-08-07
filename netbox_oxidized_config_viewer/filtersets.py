from netbox.filtersets import NetBoxModelFilterSet
from .models import OxidizedConfigViewer


# class OxidizedConfigViewerFilterSet(NetBoxModelFilterSet):
#
#     class Meta:
#         model = OxidizedConfigViewer
#         fields = ['name', ]
#
#     def search(self, queryset, name, value):
#         return queryset.filter(description__icontains=value)
