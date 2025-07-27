# Create your models here.
from django.db import models
from pydantic import BaseModel, ValidationError
from .config import SIMILARITY_THRESHHOLD, MODEL_NAME, MODEL_KWARGS, ENCODE_KWARGS, COLLECTION_NAME
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore

def embedding_for_risk(risk):
    """
    Embeds a single Risk object and adds it to the Qdrant collection.
    """
    embedding_model = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=MODEL_KWARGS,
        encode_kwargs=ENCODE_KWARGS
    )

    print("setup HuggingFaceEmbeddings")
    client = QdrantClient(path="qdrant.db")
    print("setup QdrantClient")

    vector_store = QdrantVectorStore(
        client = client,
        collection_name = COLLECTION_NAME,
        embedding = embedding_model
    )

    print("setup QdrantVectorStore")
    
    vector_store.add_texts(
        texts=[risk.description],
        ids=[risk.id]
    )
    
    print(f"embedding for risk {risk.id} done")


def check_risk_similarity(text):
    """
    If the risk description is similar to an existing risk, return False.
    Otherwise, return True.
    """
    embedding_model = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=MODEL_KWARGS,
        encode_kwargs=ENCODE_KWARGS
    )
    print("setup HuggingFaceEmbeddings")
    client = QdrantClient(path="qdrant.db")
    print("setup QdrantClient")
    vectore_store = QdrantVectorStore(
        client = client,
        collection_name = COLLECTION_NAME,
        embedding = embedding_model 
    )
    print("setup QdrantVectorStore")
    similaritys = vectore_store.similarity_search_with_relevance_scores(text, k=5)
    # print([score for _, score in similaritys])
    for risk, score in similaritys:
        if score > SIMILARITY_THRESHHOLD:
            print(f"Risk description is similar to existing risk: {risk} with score {score}")
            return False
    
    return True

def validate_https(value):
    if value and not value.startswith("https://"):
        raise ValidationError("URL must start with 'https://'")

class Risk(models.Model):
    RISK_TYPE_CHOICES = [
        (0, 'Geopolitical Risk'),
        (1, 'Environmental Risk'),
        (2, 'Logistics Risk'),
        (3, 'Weather Risk'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    risk_level = models.CharField(max_length=50, choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')])
    risk_score = models.FloatField(default=0.0)
    url = models.URLField(blank=True, null=True, validators=[validate_https])
    source = models.CharField(blank=True, null=True)
    risk_type = models.IntegerField(
        choices=RISK_TYPE_CHOICES,
        default=0
    )

    def save(self, *args, **kwargs):
        no_similar_risks = check_risk_similarity(self.description)
        if no_similar_risks:
            embedding_for_risk(self)
            super().save(*args, **kwargs)
            print(f"Name: {self.name[:255]}, Description: {self.description}, Risk Level: {self.risk_level.lower()}, Risk Score: {self.risk_score}, Url: {self.url}, Node ID: {self.node_id}")
        else:
            print(f"Risk {self.name[:255]} is similar to an existing risk, not saving.")

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