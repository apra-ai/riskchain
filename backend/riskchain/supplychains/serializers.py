# myapp/serializers.py
from rest_framework import serializers
from .models import SupplyChain, Node, Edge

class NodeSerializer(serializers.ModelSerializer):
    risks = serializers.StringRelatedField(many=True)

    class Meta:
        model = Node
        fields = ('id', 'name', 'type', 'description', 'status', 'risks')


class EdgeSerializer(serializers.ModelSerializer):
    from_node = serializers.StringRelatedField()
    to_node = serializers.StringRelatedField()
    risks = serializers.StringRelatedField(many=True)

    class Meta:
        model = Edge
        fields = (
            'id',
            'from_node',
            'to_node',
            'transport_description',
            'mode',
            'time',
            'cost',
            'status',
            'risks',
        )

class SupplyChainSerializer(serializers.ModelSerializer):
    nodes = NodeSerializer(many=True, read_only=True)
    edges = EdgeSerializer(many=True, read_only=True)
    total_risk = serializers.FloatField(read_only=True)
    risk_level = serializers.CharField(read_only=True)

    class Meta:
        model = SupplyChain
        fields = (
            'id',
            'name',
            'description',
            'nodes',
            'edges',
            'total_risk',
            'risk_level',
            'last_updated',
        )
