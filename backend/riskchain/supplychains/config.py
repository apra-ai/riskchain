COLLECTION_NAME = "risk-description-embeddings"
MODEL_NAME = "all-mpnet-base-v2"
MODEL_KWARGS = {'device': 'cpu'}
ENCODE_KWARGS = {'normalize_embeddings': False}
SIMILARITY_THRESHHOLD = 0.95