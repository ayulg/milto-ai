"""
add_embeddings.py - Add embeddings and vector search
"""

import json
import numpy as np
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    HAS_ST = True
except ImportError:
    HAS_ST = False
    print("⚠️ Install: pip install sentence-transformers")

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    print("⚠️ Install: pip install faiss-cpu")

DATA_DIR = Path("data")
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = Path("models")
EMBEDDINGS_DIR = MODELS_DIR / "embeddings"
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

def load_careers():
    """Load career data"""
    file_path = PROCESSED_DIR / "unified_careers.json"
    if not file_path.exists():
        file_path = PROCESSED_DIR / "esco_occupations.json"
    if not file_path.exists():
        file_path = DATA_DIR / "milto" / "careers.json"
    
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    
    print("❌ No career data found!")
    return []

def create_document_text(career):
    """Create searchable document text from career"""
    parts = [
        career.get('title', ''),
        career.get('description', ''),
        ' '.join(career.get('skills', [])),
        ' '.join(career.get('activities', []))
    ]
    return ' '.join([p for p in parts if p and str(p) != 'nan'])

def build_embeddings():
    """Build and save embeddings"""
    print("\n" + "="*60)
    print("🔍 BUILDING CAREER EMBEDDINGS")
    print("="*60)
    
    if not HAS_ST:
        print("❌ sentence-transformers not installed")
        print("   Install: pip install sentence-transformers")
        return None
    
    careers = load_careers()
    if not careers:
        print("❌ No careers loaded!")
        return None
    
    print(f"   Loading {len(careers)} careers")
    
    # Create documents
    documents = [create_document_text(c) for c in careers]
    documents = [d for d in documents if d.strip()]
    
    if not documents:
        print("❌ No documents created!")
        return None
    
    print(f"   Created {len(documents)} documents")
    
    # Load model
    print("   Loading embedding model...")
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
    
    # Generate embeddings
    print("   Generating embeddings...")
    try:
        embeddings = model.encode(documents, show_progress_bar=True)
        embeddings = np.array(embeddings)
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return None
    
    print(f"✅ Created embeddings: {embeddings.shape}")
    
    # Save embeddings
    np.save(EMBEDDINGS_DIR / 'career_embeddings.npy', embeddings)
    
    # Save metadata
    metadata = {
        'model': 'all-MiniLM-L6-v2',
        'embedding_dim': embeddings.shape[1],
        'num_careers': len(careers),
        'career_ids': [c.get('id', f'c_{i}') for i, c in enumerate(careers) if c.get('id')]
    }
    
    with open(EMBEDDINGS_DIR / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Saved to: {EMBEDDINGS_DIR}")
    
    # Build FAISS index
    if HAS_FAISS:
        build_faiss_index(embeddings, careers)
    
    return embeddings

def build_faiss_index(embeddings, careers):
    """Build FAISS index for fast search"""
    print("\n🔍 Building FAISS index...")
    
    try:
        # Normalize for cosine similarity
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Build index
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings_norm.astype(np.float32))
        
        # Save
        faiss.write_index(index, str(EMBEDDINGS_DIR / 'career_index.faiss'))
        print(f"✅ FAISS index saved")
        
    except Exception as e:
        print(f"⚠️ Error building FAISS index: {e}")

def main():
    print("="*60)
    print("🚀 MILTO - ADD EMBEDDINGS")
    print("="*60)
    
    embeddings = build_embeddings()
    
    if embeddings is not None:
        print("\n" + "="*60)
        print("✅ Embeddings complete!")
        print("\n📋 NEXT: Run the app")
        print("   Run: python app.py")
    else:
        print("\n⚠️ Embeddings creation failed")

if __name__ == "__main__":
    main()