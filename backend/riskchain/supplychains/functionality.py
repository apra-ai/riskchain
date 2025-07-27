from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from .models import Risk
from .config import MODEL_NAME, MODEL_KWARGS, ENCODE_KWARGS, COLLECTION_NAME

def create_collection(client):

    # Check if the collection already exists
    existing_collections = client.get_collections().collections
    if any(collection.name == COLLECTION_NAME for collection in existing_collections):
        print(f"Collection '{COLLECTION_NAME}' already existed.")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )
    print("setup QdrantClient collection")


def embedding_for_risks():
    """
    Initial embedding of all Risk objects in the database.
    This function creates a Qdrant collection and stores the embeddings of the Risk objects.
    """
    embedding_model = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=MODEL_KWARGS,
        encode_kwargs=ENCODE_KWARGS
    )

    print("setup HuggingFaceEmbeddings")
    client = QdrantClient(path="qdrant.db")
    print("setup QdrantClient")

    existing_collections = client.get_collections().collections
    if not(any(collection.name == COLLECTION_NAME for collection in existing_collections)):
        create_collection(client)

    vector_store = QdrantVectorStore(
        client = client,
        collection_name = COLLECTION_NAME,
        embedding = embedding_model
    )

    print("setup QdrantVectorStore")

    id_risks = []
    description_risks = []
    for risk in Risk.objects.all():
        id_risks.append(risk.id)
        description_risks.append(risk.description)

    print("start embedding for risks")
    vector_store.add_texts(
        texts=description_risks,
        ids=id_risks
    )

    print("embedding for risks done")

