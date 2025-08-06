# myapp/urls.py
from django.urls import path
from .views import SupplyChainDetail, SupplyChainsView, NodeDetail, NodesView, EdgeDetail, EdgesView, RiskDetail, RisksView, UpdateRisksSupplychain

urlpatterns = [
    # Path for retrieving a specific supply chain by its ID
    path('supplychain/<int:pk>/', SupplyChainDetail.as_view(), name='supplychain-detail'),
    path('supplychain', SupplyChainsView.as_view(), name='supplychains'),
    path('node/<int:pk>/', NodeDetail.as_view(), name='node-detail'),
    path('node', NodesView.as_view(), name='nodes'),
    path('edge/<int:pk>/', EdgeDetail.as_view(), name='edge-detail'),
    path('edge', EdgesView.as_view(), name='edges'),
    path('risk/<int:pk>/', RiskDetail.as_view(), name='risk-detail'),
    path('risk', RisksView.as_view(), name='risks'),
    path('generaterisks', UpdateRisksSupplychain.as_view(), name='generate-risks'),
]