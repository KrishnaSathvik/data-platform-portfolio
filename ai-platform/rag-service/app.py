#!/usr/bin/env python3
"""
RAG service for explaining fraud predictions.
Uses FAISS for vector search and sentence transformers for embeddings.
"""

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    print("❌ FastAPI not installed. Run: pip install fastapi uvicorn")
    exit(1)

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("❌ AI libraries not installed. Run: pip install sentence-transformers faiss-cpu")
    exit(1)

import os
from typing import List, Dict

app = FastAPI(title="RAG Explanation Service", version="1.0.0")

# Initialize embedding model and vector store
embedding_model = None
index = None
documents = []

class ExplanationRequest(BaseModel):
    transaction_id: str
    fraud_probability: float
    amount: float
    merchant: str
    features: Dict

class ExplanationResponse(BaseModel):
    explanation: str
    sources: List[str]
    confidence: float

def load_knowledge_base():
    """Load and index platform documentation."""
    global index, documents, embedding_model
    
    print("🧠 Loading embedding model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Sample fraud detection knowledge
    documents = [
        "High transaction amounts above $500 are often indicators of fraud.",
        "Merchants with suspicious names or unknown locations increase fraud risk.",
        "Credit card transactions from new devices have higher fraud probability.",
        "Multiple transactions from the same user in short time periods indicate fraud.",
        "Transactions outside normal business hours are suspicious.",
        "Payment methods like prepaid cards are higher risk for fraud."
    ]
    
    # Create embeddings and FAISS index
    print("📚 Creating document embeddings...")
    embeddings = embedding_model.encode(documents)
    
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype('float32'))
    
    print(f"✅ Loaded {len(documents)} documents into knowledge base")

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup."""
    load_knowledge_base()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "documents_loaded": len(documents),
        "index_ready": index is not None
    }

@app.post("/explain", response_model=ExplanationResponse)
async def explain_prediction(request: ExplanationRequest):
    """Generate explanation for fraud prediction."""
    if index is None or embedding_model is None:
        raise HTTPException(status_code=500, detail="Knowledge base not loaded")
    
    # Create query from transaction features
    query = f"fraud prediction amount {request.amount} merchant {request.merchant}"
    
    # Find relevant documents
    query_embedding = embedding_model.encode([query])
    
    # Search for top 3 most relevant documents
    scores, indices = index.search(query_embedding.astype('float32'), k=3)
    
    relevant_docs = [documents[i] for i in indices[0]]
    confidence = float(np.mean(scores[0]))
    
    # Generate explanation (mock - replace with actual LLM)
    if request.fraud_probability > 0.7:
        explanation = f"HIGH FRAUD RISK: This transaction shows multiple risk factors. "
    elif request.fraud_probability > 0.3:
        explanation = f"MODERATE FRAUD RISK: Some suspicious patterns detected. "
    else:
        explanation = f"LOW FRAUD RISK: Transaction appears normal. "
    
    explanation += f"Amount of ${request.amount} from merchant '{request.merchant}' "
    explanation += f"has {request.fraud_probability:.1%} fraud probability."
    
    return ExplanationResponse(
        explanation=explanation,
        sources=relevant_docs,
        confidence=min(confidence / 10, 1.0)  # Normalize confidence
    )

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except ImportError:
        print("❌ uvicorn not installed. Run: pip install uvicorn")
