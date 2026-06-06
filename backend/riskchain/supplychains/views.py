"""REST API views for browsing supply chains and triggering risk updates."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import SupplyChain, Node, Edge, Risk
from .serializers import SupplyChainSerializer, NodeSerializer, EdgeSerializer, RiskSerializer
from agents.orchestrator_agent import process_node_with_supervisor, process_edge_with_supervisor


class SupplyChainDetail(APIView):
    """Return a single supply chain with its related structure."""

    def get(self, request, pk, format=None):
        """Fetch one supply chain by primary key."""

        try:
            supply_chain = SupplyChain.objects.get(pk=pk)
            serializer = SupplyChainSerializer(supply_chain)
            return Response(serializer.data)
        except SupplyChain.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class SupplyChainsView(APIView):
    """Return the list of available supply chains."""

    def get(self, request, format=None):
        """Fetch all stored supply chains."""

        supply_chains = SupplyChain.objects.all()
        serializer = SupplyChainSerializer(supply_chains, many=True)
        return Response(serializer.data)


class NodeDetail(APIView):
    """Return a single node in the supply chain graph."""

    def get(self, request, pk, format=None):
        """Fetch one node by primary key."""

        try:
            node = Node.objects.get(pk=pk)
            serializer = NodeSerializer(node)
            return Response(serializer.data)
        except Node.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class NodesView(APIView):
    """Return the list of all registered nodes."""

    def get(self, request, format=None):
        """Fetch all nodes used across supply chains."""

        nodes = Node.objects.all()
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)


class EdgeDetail(APIView):
    """Return a single transport edge between two nodes."""

    def get(self, request, pk, format=None):
        """Fetch one edge by primary key."""

        try:
            edge = Edge.objects.get(pk=pk)
            serializer = EdgeSerializer(edge)
            return Response(serializer.data)
        except Edge.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class EdgesView(APIView):
    """Return the list of all transport edges."""

    def get(self, request, format=None):
        """Fetch all edges used in the supply chain graph."""

        edges = Edge.objects.all()
        serializer = EdgeSerializer(edges, many=True)
        return Response(serializer.data)


class RiskDetail(APIView):
    """Return a single stored risk record."""

    def get(self, request, pk, format=None):
        """Fetch one risk by primary key."""

        try:
            risk = Risk.objects.get(pk=pk)
            serializer = RiskSerializer(risk)
            return Response(serializer.data)
        except Risk.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class RisksView(APIView):
    """Return all currently stored risk records."""

    def get(self, request, format=None):
        """Fetch all risk entries created by the system."""

        risks = Risk.objects.all()
        serializer = RiskSerializer(risks, many=True)
        return Response(serializer.data)


class UpdateRisksSupplychain(APIView):
    """Trigger a risk refresh for every node and edge in one supply chain."""

    def post(self, request, format=None):
        """Run the orchestrator for the selected supply chain and persist new risks."""

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
