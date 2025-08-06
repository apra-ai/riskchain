# myapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SupplyChain, Node, Edge, Risk
from .serializers import SupplyChainSerializer, NodeSerializer, EdgeSerializer, RiskSerializer
from agents.orchestrator_agent import process_node_with_supervisor, process_edge_with_supervisor

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

class RiskDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            risk = Risk.objects.get(pk=pk)
            serializer = RiskSerializer(risk)
            return Response(serializer.data)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class RisksView(APIView):
    def get(self, request, format=None):
        try:
            risks = Risk.objects.all()
            serializer = RiskSerializer(risks, many=True)
            return Response(serializer.data)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class UpdateRisksSupplychain(APIView):
    def post(self, request, format=None):
        data = request.data
        supplychain_id = data.get('supply_chain_id')
        if not supplychain_id:
            return Response({"detail": "Supply chain ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        supplychain = SupplyChain.objects.filter(id=supplychain_id).first()
        if not supplychain:
            return Response({"detail": "Supply chain not found."}, status=status.HTTP_404_NOT_FOUND)

        for node in supplychain.nodes.all():
            process_node_with_supervisor(node)

        for edge in supplychain.edges.all():
            process_edge_with_supervisor(edge)

        return Response({"detail": f"Risk for supplychain {supplychain_id} updated."})
