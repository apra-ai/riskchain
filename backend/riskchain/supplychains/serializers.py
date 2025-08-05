# myapp/serializers.py
from rest_framework import serializers
from .models import SupplyChain, Node, Edge

class NodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Node
        fields = ('id', 'name', 'type', 'description', 'status', 'risks')


class EdgeSerializer(serializers.ModelSerializer):
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
