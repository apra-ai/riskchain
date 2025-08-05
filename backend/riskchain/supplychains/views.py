# myapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SupplyChain, Node, Edge
from .serializers import SupplyChainSerializer, NodeSerializer, EdgeSerializer

class SupplyChainDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            supply_chain = SupplyChain.objects.get(pk=pk)
            serializer = SupplyChainSerializer(supply_chain)
            return Response(serializer.data)
        except SupplyChain.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class SupplyChainsView(APIView):
    def get(self, request, format=None):
        try:
            # Get the supply chain instance by its primary key (pk)
            supply_chains = SupplyChain.objects.all()
            serializer = SupplyChainSerializer(supply_chains, many=True)
            return Response(serializer.data)
        except supply_chains.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class NodeDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            node = Node.objects.get(pk=pk)
            serializer = NodeSerializer(node)
            return Response(serializer.data)
        except node.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class NodesView(APIView):
    def get(self, request, format=None):
        try:
            nodes = Node.objects.all()
            serializer = NodeSerializer(nodes, many=True)
            return Response(serializer.data)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class EdgeDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            edge = Edge.objects.get(pk=pk)
            serializer = EdgeSerializer(edge)
            return Response(serializer.data)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class EdgesView(APIView):
    def get(self, request, format=None):
        try:
            edges = Edge.objects.all()
            serializer = EdgeSerializer(edges, many=True)
            return Response(serializer.data)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)