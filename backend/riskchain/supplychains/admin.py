from django.contrib import admin
from .models import Node, Edge, Risk, SupplyChain

# Register the models with the admin interface
admin.site.register(Node)
admin.site.register(Edge)
admin.site.register(Risk)
admin.site.register(SupplyChain)