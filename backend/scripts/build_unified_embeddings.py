import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

BACKEND_DIR = Path(__file__).resolve().parent.parent
SOURCE_FILE = BACKEND_DIR / "data" / "processed" / "unified_careers_v2.json"
OUTPUT_DIR = BACKEND_DIR / "data" / "processed" / "embeddings_unified_v1"
TEMP_DIR = BACKEND_DIR / "data" / "processed" / ".embeddings_unified_v1.tmp"

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64

def main():
    print("\n--- MILTO AI: EXPANDED EMBEDDING BUILDER ---")

    if OUTPUT_DIR.exists():
        raise FileExistsError(
            f"Output already exists. Nothing overwritten: {OUTPUT_DIR}"
        )

    if TEMP_DIR.exists():
        raise FileExistsError(
            f"Temporary directory already exists. Inspect it first: {TEMP_DIR}"
        )

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(SOURCE_FILE)

    with SOURCE_FILE.open("r", encoding="utf-8") as f:
        careers = json.load(f)

    if not isinstance(careers, list) or not careers:
        raise ValueError("Career dataset must be a non-empty list.")

    career_ids = []
    documents = []

    for position, career in enumerate(careers):
        career_id = str(career.get("id") or "").strip()
        title = str(career.get("title") or "").strip()
        description = str(career.get("description") or "").strip()
        skills = career.get("skills") or []

        if not career_id or not title or not description:
            raise ValueError(
                f"Missing ID, title, or description at record {position}"
            )

        if not isinstance(skills, list):
            raise ValueError(
                f"Invalid skills format for career: {career_id}"
            )

        skill_text = ", ".join(
            str(skill).strip()
            for skill in skills
            if isinstance(skill, str) and skill.strip()
        )

        document = (
            f"Career: {title}. "
            f"Description: {description}. "
            f"Skills: {skill_text}"
        )

        career_ids.append(career_id)
        documents.append(document)

    if len(set(career_ids)) != len(career_ids):
        raise ValueError("Duplicate career IDs detected.")

    print("Source careers:", len(careers))
    print("Prepared documents:", len(documents))
    print("Loading model:", MODEL_NAME)

    model = SentenceTransformer(MODEL_NAME, device="cpu")

    print("\nGenerating embeddings. Please wait...")

    vectors = model.encode(
        documents,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    vectors = np.asarray(vectors, dtype=np.float32)

    if vectors.ndim != 2 or vectors.shape[0] != len(careers):
        raise ValueError(f"Invalid embedding shape: {vectors.shape}")

    if not np.isfinite(vectors).all():
        raise ValueError("Embeddings contain NaN or infinity.")

    norms = np.linalg.norm(vectors, axis=1)

    if not np.allclose(norms, 1.0, atol=1e-4):
        raise ValueError("Embeddings are not correctly normalized.")

    dimension = vectors.shape[1]

    print("\nBuilding FAISS index...")
    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)

    if index.ntotal != len(careers):
        raise ValueError("FAISS index count does not match career count.")

    TEMP_DIR.mkdir(parents=True)

    np.save(TEMP_DIR / "career_embeddings.npy", vectors)
    faiss.write_index(index, str(TEMP_DIR / "career_index.faiss"))

    metadata = {
        "model": MODEL_NAME,
        "embedding_dim": dimension,
        "num_careers": len(career_ids),
        "career_ids": career_ids,
        "source_dataset": "unified_careers_v2.json",
        "index_type": "IndexFlatIP",
        "normalized_embeddings": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": hashlib.sha256(
            SOURCE_FILE.read_bytes()
        ).hexdigest(),
    }

    with (TEMP_DIR / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Reload and verify the saved index before publishing the directory.
    saved_index = faiss.read_index(str(TEMP_DIR / "career_index.faiss"))
    saved_vectors = np.load(TEMP_DIR / "career_embeddings.npy")

    if saved_index.ntotal != len(career_ids):
        raise ValueError("Saved FAISS index failed verification.")

    if saved_vectors.shape != vectors.shape:
        raise ValueError("Saved NumPy embeddings failed verification.")

    TEMP_DIR.rename(OUTPUT_DIR)

    print("\n--- BUILD COMPLETED ---")
    print("Careers indexed:", len(career_ids))
    print("Embedding dimension:", dimension)
    print("FAISS vectors:", saved_index.ntotal)
    print("Output directory:", OUTPUT_DIR)
    print("Original 28-career index was not modified.")

if __name__ == "__main__":
    main()
