import os
import re

import chromadb
import yaml
from sentence_transformers import SentenceTransformer

MD_FOLDER = "md"
CHROMA_PATH = "chroma_db"
COLLECTION = "fermentacija"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Izdvaja YAML frontmatter i vraća (metadata, body)."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
                return meta, parts[2].strip()
            except yaml.YAMLError:
                pass
    return {}, text.strip()


def split_by_headings(body: str) -> list[str]:
    """Dijeli tekst na sekcije po Markdown naslovima."""
    pattern = re.compile(r"(?=^#{1,3} .+)", re.MULTILINE)
    sections = pattern.split(body)
    return [s.strip() for s in sections if s.strip()]


def chunk_section(section: str, size: int, overlap: int) -> list[str]:
    """Dijeli dugu sekciju na chunkove s preklapanjem."""
    if len(section) <= size:
        return [section]

    chunks = []
    start = 0
    while start < len(section):
        end = start + size
        chunk = section[start:end]
        chunks.append(chunk)
        start += size - overlap
    return chunks


def load_documents(folder: str) -> list[dict]:
    """Učitava sve .md fajlove i vraća listu {meta, chunks, filename}."""
    md = []
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(folder, fname)
        with open(path, encoding="utf-8") as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)
        sections = split_by_headings(body)

        all_chunks = []
        for sec in sections:
            all_chunks.extend(chunk_section(sec, CHUNK_SIZE, CHUNK_OVERLAP))

        md.append(
            {
                "filename": fname,
                "meta": meta,
                "chunks": all_chunks,
            }
        )
        print(f"  OK {fname} - {len(all_chunks)} chunk(a)")
    return md


def build_chroma(md: list[dict]) -> chromadb.Collection:
    """Vektorizira chunkove i sprema ih u ChromaDB."""
    print(f"\nUčitavam embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection(COLLECTION)
        print(f"Stara kolekcija '{COLLECTION}' obrisana.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    ids, texts, metadatas = [], [], []

    for doc in md:
        fname = doc["filename"]
        meta = doc["meta"]
        tags = ", ".join(meta.get("tags", []))

        for chunk_idx, chunk in enumerate(doc["chunks"]):
            chunk_id = f"{fname}_{chunk_idx}"
            ids.append(chunk_id)
            texts.append(chunk)
            metadatas.append(
                {
                    "filename": fname,
                    "title": meta.get("title", ""),
                    "source_type": meta.get("source_type", ""),
                    "tags": tags,
                    "chunk_index": chunk_idx,
                }
            )

    print(f"\nVektoriziram {len(texts)} chunkova...")
    embeddings_list = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings_list,
        metadatas=metadatas,
    )

    print(f"\nChromaDB kolekcija '{COLLECTION}' kreirana s {len(ids)} chunkova.")
    print(f"   Lokacija: {os.path.abspath(CHROMA_PATH)}")
    return collection


def demo_retrieval(collection: chromadb.Collection, model: SentenceTransformer):
    """Brzi test: prikazuje top-3 chunkove za primjerno pitanje."""
    query = "Na površini kombuche pojavila se crna plijesan. Što trebam napraviti?"
    print("\nDemo retrieval")
    print(f"Upit: {query}\n")

    q_emb = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=q_emb,
        n_results=3,
        include=["documents", "metadatas", "distances"],
    )

    for i, (doc, meta, dist) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ):
        score = round(1 - dist, 4)
        print(f"[Chunk {i+1}] Sličnost: {score}  |  Izvor: {meta['filename']}")
        print(f"Naslov dokumenta: {meta['title']}")
        print(f"Tagovi: {meta['tags']}")
        print(f"Tekst: {doc[:300]}{'...' if len(doc) > 300 else ''}")
        print()


if __name__ == "__main__":
    print("-" * 60)
    print("  RAG INGEST - Chatbot za kućnu fermentaciju")
    print("-" * 60)
    print(f"\nUčitavam dokumente iz: {os.path.abspath(MD_FOLDER)}\n")

    md = load_documents(MD_FOLDER)
    print(f"\nUkupno dokumenata: {len(md)}")

    collection = build_chroma(md)

    model = SentenceTransformer(EMBED_MODEL)
    demo_retrieval(collection, model)
