from django.contrib import admin
from .models import Node, Edge, Risk, SupplyChain, Country, City

# Register the models with the admin interface
# admin.site.register(Node)
# admin.site.register(Edge)
# admin.site.register(Risk)
# admin.site.register(SupplyChain)

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("country", "city")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "city" and request.POST.get("country"):
            country_id = request.POST.get("country")
            kwargs["queryset"] = City.objects.filter(country_id=country_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)