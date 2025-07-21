# Create your models here.
from django.db import models

def validate_https(value):
    if value and not value.startswith("https://"):
        raise ValidationError("URL must start with 'https://'")

class Risk(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    risk_level = models.CharField(max_length=50, choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')])
    risk_score = models.FloatField(default=0.0)
    source = models.URLField(blank=True, null=True, validators=[validate_https])

    def __str__(self):
        return self.name

class Node(models.Model):
    name = models.CharField(max_length=255)  
    type = models.CharField(max_length=255)  
    description = models.TextField()  
    status = models.CharField(max_length=50, choices=[('completed', 'Completed'), ('active', 'Active'), ('pending', 'Pending')])  

    risks = models.ManyToManyField(Risk, related_name='nodes')

    def __str__(self):
        return self.name

class Edge(models.Model):
    from_node = models.ForeignKey(Node, related_name='outgoing_edges', on_delete=models.CASCADE)  
    to_node = models.ForeignKey(Node, related_name='incoming_edges', on_delete=models.CASCADE)  
    transport_description = models.CharField(max_length=255)  
    mode = models.CharField(max_length=255)  # e.g. Shipping or Truck
    time = models.CharField(max_length=255)  
    cost = models.FloatField()  
    status = models.CharField(max_length=50, choices=[('completed', 'Completed'), ('active', 'Active'), ('pending', 'Pending')])  

    # Many-to-many relationship with the Risk model
    risks = models.ManyToManyField(Risk, related_name='edges')

    def __str__(self):
        return f"{self.from_node.name} -> {self.to_node.name} ({self.transport_description})"

class SupplyChain(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    nodes = models.ManyToManyField(Node, related_name='supply_chains')
    edges = models.ManyToManyField(Edge, related_name='supply_chains')
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def total_risk(self):
        risk_scores = []

        for node in self.nodes.all():
            for risk in node.risks.all():
                score = risk.risk_score
                risk_scores.append(score)
        for edge in self.edges.all():
            for risk in edge.risks.all():
                score = risk.risk_score
                risk_scores.append(score)

        if not risk_scores:
            return 0.0
        
        return round(sum(risk_scores) / len(risk_scores), 2)

    @property
    def risk_level(self):
        score = self.total_risk
        if score >= 0.7:
            return "High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low"

    def __str__(self):
        return self.name