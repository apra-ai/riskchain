# myapp/urls.py
from django.urls import path
from .views import SupplyChainDetail, SupplyChains

urlpatterns = [
    # Path for retrieving a specific supply chain by its ID
    path('supplychain/<int:pk>/', SupplyChainDetail.as_view(), name='supplychain-detail'),
    path('supplychain', SupplyChains.as_view(), name='supplychains'),
]