# myapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SupplyChain
from .serializers import SupplyChainSerializer

class SupplyChainDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            supply_chain = SupplyChain.objects.get(pk=pk)
            serializer = SupplyChainSerializer(supply_chain)
            return Response(serializer.data)
        except SupplyChain.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class SupplyChains(APIView):
    def get(self, request, format=None):
        try:
            # Get the supply chain instance by its primary key (pk)
            supply_chains = SupplyChain.objects.all()
            serializer = SupplyChainSerializer(supply_chains, many=True)
            return Response(serializer.data)
        except SupplyChain.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)