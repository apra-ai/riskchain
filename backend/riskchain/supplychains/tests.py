# tests.py

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from supplychains.models import SupplyChain, Node, Edge, Risk

class SupplyChainAPITests(APITestCase):

    def setUp(self):
        """
        Set up test data for the tests.
        """
        # Erstelle eine Node
        node = Node.objects.create(name="Node1", type="Type1", description="Description", status="active")
        
        # Erstelle einen Risk
        risk = Risk.objects.create(name="Risk1", description="Risk Description", risk_level="high", risk_score=0.8)
        if risk.id is not None:
            node.risks.add(risk)

        # Erstelle eine Edge
        edge = Edge.objects.create(from_node=node, to_node=node, transport_description="Shipping", mode="Truck", time="1 day", cost=100.0, status="completed")
        
        # Erstelle ein SupplyChain-Objekt
        supply_chain = SupplyChain.objects.create(name="Supply Chain 1", description="Supply chain description")
        supply_chain.nodes.add(node)
        supply_chain.edges.add(edge)
        
        self.supply_chain = supply_chain

    def test_get_supply_chain_detail(self):
        """
        Test: GET /supplychain/<id> should return the details of a specific supply chain.
        """
        url = reverse('supplychain-detail', args=[self.supply_chain.id])

        response = self.client.get(url)

        # Überprüfen, ob der Statuscode 200 ist
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Überprüfen, ob die erwarteten Daten im Response sind
        self.assertEqual(response.data['id'], self.supply_chain.id)
        self.assertEqual(response.data['name'], self.supply_chain.name)
        self.assertEqual(response.data['description'], self.supply_chain.description)

    def test_get_supply_chains(self):
        """
        Test: GET /supplychain should return a list of all supply chains.
        """
        url = reverse('supplychains')  # Der URL-Name aus deiner urls.py
        response = self.client.get(url)

        # Überprüfen, ob der Statuscode 200 ist
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Überprüfen, ob die Antwort die korrekten Daten enthält
        self.assertGreater(len(response.data), 0)  # Sicherstellen, dass mindestens ein Supply Chain zurückgegeben wird
        self.assertIn('id', response.data[0])  # Überprüfen, ob das erste Element eine 'id' enthält
        self.assertIn('name', response.data[0])  # Überprüfen, ob das erste Element einen 'name' enthält
