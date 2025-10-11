from django.contrib import admin
from .models import Node, Edge, Risk, SupplyChain, Country, City, ChainStep
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet


# -----------------------------
# INLINE: ChainSteps in SupplyChain anzeigen
# -----------------------------
class ChainStepInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        steps = []

        # Alle gültigen ChainSteps einsammeln
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("edge") is None or form.cleaned_data.get("position") is None:
                continue
            steps.append((form.cleaned_data["position"], form.cleaned_data["edge"]))

        # Nach Position sortieren (1, 2, 3, ...)
        steps.sort(key=lambda x: x[0])

        # Optional: prüfen, ob Positionen fortlaufend sind
        if steps and steps[0][0] != 1:
            raise ValidationError("Die Kette muss bei Position 1 beginnen.")
        for i in range(len(steps)-1):
            if steps[i+1][0] != steps[i][0] + 1:
                raise ValidationError("Positionen müssen fortlaufend sein (1..N) – Lücke gefunden.")

        # 🧠 HIER der eigentliche Check:
        # Step n → to_node == Step n+1 → from_node ?
        for (pos_a, edge_a), (pos_b, edge_b) in zip(steps, steps[1:]):
            if edge_a.to_node_id != edge_b.from_node_id:
                raise ValidationError(
                    f"Ungültiger Übergang: Step {pos_a} endet bei "
                    f"{edge_a.to_node.city} – Step {pos_b} startet bei "
                    f"{edge_b.from_node.city}."
                )

class ChainStepInline(admin.TabularInline):
    model = ChainStep
    formset = ChainStepInlineFormSet
    extra = 0
    ordering = ("position",)
    fields = ("position", "edge")
    autocomplete_fields = ("edge",)

# -----------------------------
# SupplyChain Admin
# -----------------------------
@admin.register(SupplyChain)
class SupplyChainAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "step_count")
    search_fields = ("name",)
    inlines = [ChainStepInline]

    def step_count(self, obj):
        return obj.steps.count()
    step_count.short_description = "Steps"


# -----------------------------
# Edge Admin
# -----------------------------
@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ("from_node", "to_node", "transport_modes", "crosses_border", "cost", "reliability", "distance")
    list_filter = ("transport_modes", "crosses_border", "cost", "reliability", "distance")
    search_fields = (
        "from_node__city__name", "from_node__country__name",
        "to_node__city__name", "to_node__country__name",
    )
    list_select_related = ("from_node__country", "to_node__country")
    autocomplete_fields = ("from_node", "to_node")
    filter_horizontal = ("risks",)


# -----------------------------
# Node Admin (mit City-Filter)
# -----------------------------
@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("country", "city", "node_role", "ownership", "capacity_class")
    list_filter = ("country", "node_role", "ownership", "capacity_class")
    search_fields = ("city__name", "country__name")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "city" and request.POST.get("country"):
            country_id = request.POST.get("country")
            kwargs["queryset"] = City.objects.filter(country_id=country_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# -----------------------------
# Optional: Country & City registrieren
# -----------------------------
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)
    search_fields = ("name", "country__name")


# -----------------------------
# Risk optional (nur wenn du brauchst)
# -----------------------------
@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ("name", "risk_level", "risk_type", "risk_score")
    list_filter = ("risk_level", "risk_type")
    search_fields = ("name", "description")
