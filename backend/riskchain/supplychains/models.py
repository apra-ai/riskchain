# Create your models here.
from django.db import models
from pydantic import BaseModel, ValidationError
from .config import SIMILARITY_THRESHHOLD, MODEL_NAME, MODEL_KWARGS, ENCODE_KWARGS, COLLECTION_NAME
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from smart_selects.db_fields import ChainedForeignKey
from .data_structure import NODE_ROLE_CHOICES, OWNERSHIP_CHOICES, CAPACITY_CLASS_CHOICES, TRANSPORT_MODES_CHOICES, CROSSES_BORDER, COST_CLASS, RELIABILITY_CLASS, DISTANCE_CLASS

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

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    class Meta:
        unique_together = ('name', 'country')

    def __str__(self):
        return f"{self.name} ({self.country.name})"

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
    url = models.URLField(blank=True, null=True, validators=[validate_https])
    source = models.CharField(blank=True, null=True)
    risk_type = models.IntegerField(
        choices=RISK_TYPE_CHOICES,
        default=0
    )

    # def save(self, *args, **kwargs):
    #     no_similar_risks = check_risk_similarity(self.description)
    #     if no_similar_risks:
    #         super().save(*args, **kwargs)
    #         embedding_for_risk(self)
    #         print(f"Name: {self.name[:255]}, Description: {self.description}, Risk Level: {self.risk_level.lower()}, Risk Score: {self.risk_score}, Url: {self.url}, Node ID: {self.node_id}")
    #     else:
    #         print(f"Risk is similar to an existing risk, not saving.")

    def __str__(self):
        return self.name

class Node(models.Model):
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    delay_score = models.FloatField(default=1.0, editable=False)
    city = ChainedForeignKey(
        City,
        chained_field="country",
        chained_model_field="country",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT
    )

    node_role = models.CharField(
        max_length=30,
        choices=NODE_ROLE_CHOICES,
        default="SUPPLIER"
    )

    ownership = models.CharField(
        max_length=30,
        choices=OWNERSHIP_CHOICES,
        default="SUPPLIER"
    )

    capacity_class = models.CharField(
        max_length=30,
        choices=CAPACITY_CLASS_CHOICES,
        default="SUPPLIER"
    )

    risks = models.ManyToManyField(Risk, related_name='nodes', blank=True)

    def onehot(self, encoder: "NodeOneHotEncoder"):   # <- String statt Import
        return encoder.encode(self)

    def __str__(self):
        return f"{self.country}({self.city})"



class Edge(models.Model):
    from_node = models.ForeignKey(Node, related_name='outgoing_edges', on_delete=models.CASCADE)  
    to_node = models.ForeignKey(Node, related_name='incoming_edges', on_delete=models.CASCADE)
    delay_score = models.FloatField(default=1.0, editable=False)

    crosses_border = models.CharField(
        max_length=30,
        choices=CROSSES_BORDER,
        default="SUPPLIER"
    )

    transport_modes = models.CharField(
        max_length=30,
        choices=TRANSPORT_MODES_CHOICES,
        default="SUPPLIER"
    )

    cost = models.CharField(
        max_length=30,
        choices=COST_CLASS,
        default="SUPPLIER"
    )

    reliability = models.CharField(
        max_length=30,
        choices=RELIABILITY_CLASS,
        default="SUPPLIER"
    )

    distance = models.CharField(
        max_length=30,
        choices=DISTANCE_CLASS,
        default="SUPPLIER"
    )

    # Many-to-many relationship with the Risk model
    risks = models.ManyToManyField(Risk, related_name='edges', blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(from_node=models.F("to_node")),
                name="edge_no_self_loop",
            )
        ]
    
    def onehot(self, encoder: "EdgeOneHotEncoder"):
        return encoder.encode(self)

    def __str__(self):
        return f"({self.from_node}) -> ({self.to_node}), ({self.transport_modes})"


class SupplyChain(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    predicted_delay = models.FloatField(blank=True, null=True, editable=False)

    def __str__(self):
        return f"{self.name}"

    def get_delay_score(self):
        supply_duration_days = 0
        for step in self.steps.all():
            supply_duration_days += step.edge.delay_score
        return supply_duration_days

    def steps_ordered(self):
        # korrektes Vorladen über die Edge → from_node/to_node + Länder
        return (
            self.steps
            .select_related(
                "edge__from_node__country",
                "edge__to_node__country",
            )
            .order_by("position")
        )

    # optional, aber empfohlen: Konsistenzprüfung der Kette
    def clean(self):
        # Beim Anlegen (ohne PK) KEINE Steps prüfen
        if not self.pk:
            return

        steps = list(self.steps_ordered())
        if not steps:
            return

        if steps[0].position != 1:
            raise ValidationError("Die Kette muss bei Position 1 beginnen.")
        for i in range(len(steps) - 1):
            if steps[i+1].position != steps[i].position + 1:
                raise ValidationError("Positionen müssen fortlaufend sein (1..N).")
        for a, b in zip(steps, steps[1:]):
            if a.edge.to_node_id != b.edge.from_node_id:
                raise ValidationError(
                    f"Übergang ungültig: Step {a.position} endet bei "
                    f"{a.edge.to_node.city} – Step {b.position} startet bei "
                    f"{b.edge.from_node.city}."
                )

class ChainStep(models.Model):
    chain = models.ForeignKey(
        SupplyChain, on_delete=models.CASCADE, related_name="steps"
    )
    position = models.PositiveIntegerField()  # 1,2,3,…
    edge = models.ForeignKey("Edge", on_delete=models.PROTECT, related_name="chain_steps")

    class Meta:
        ordering = ["position"]
        constraints = [
            # Position muss je Kette eindeutig sein
            models.UniqueConstraint(
                fields=["chain", "position"], name="uniq_chain_position"
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.chain} | {self.position}: {self.edge.from_node} → {self.edge.to_node}"