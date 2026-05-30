import json

import chromadb
import requests
from flask import Flask, jsonify, render_template, request, stream_with_context, Response
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "chroma_db"
COLLECTION = "fermentacija"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "jobautomation/OpenEuroLLM-Croatian:latest"
N_RESULTS = 4

app = Flask(__name__)

embedder = None
collection = None


def load_resources():
    global embedder, collection

    print("Učitavam embedding model...")
    embedder = SentenceTransformer(EMBED_MODEL)

    print("Spajam se na ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION)
    count = collection.count()
    print(f"Kolekcija '{COLLECTION}' učitana - {count} chunkova.")


def retrieve(query: str, n: int = N_RESULTS) -> list[dict]:
    q_emb = embedder.encode([query]).tolist()
    results = collection.query(
        query_embeddings=q_emb,
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "text": doc,
                "filename": meta.get("filename", ""),
                "title": meta.get("title", ""),
                "tags": meta.get("tags", ""),
                "score": round(1 - dist, 4),
            }
        )
    return chunks


def build_prompt(query: str, chunks: list[dict], history: list[dict]) -> list[dict]:
    context_parts = []
    for i, c in enumerate(chunks, 1):
        context_parts.append(
            f"[Izvor {i}: {c['title']} | {c['filename']}]\n{c['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    system_msg = {
        "role": "system",
        "content": (
            "Ti si chatbot za kućnu fermentaciju. Odgovaraš SAMO na pitanja "
            "vezana uz kućnu fermentaciju: kiseli kupus, kimchi, kefir, kombucha "
            "i kiselo tijesto. "
            "Pitanja izvan te domene odbij kratkom rečenicom, npr. "
            "'To pitanje nije vezano uz fermentaciju.' — bez objašnjavanja, "
            "izvlačenja, niti usmjeravanja na druge izvore. "
            "Nikad ne daješ medicinske savjete ni dijagnoze. "
            "Ako postoji opasnost po zdravlje (obojena plijesan, truli miris), "
            "jasno preporuči odbacivanje proizvoda i navedi razlog.\n\n"
            "JEZIK I STIL:\n"
            "- Uvijek odgovaraj isključivo na standardnom hrvatskom jeziku.\n"
            "- Koristi isključivo hrvatske riječi; ne koristiti anglizme, srbizme "
            "ni posuđenice kad postoji hrvatska zamjena (npr. 'kiselo tijesto' "
            "umjesto 'sourdough', 'temperatura fermentacije' umjesto 'fermentation "
            "temperature', 'šalica' umjesto 'cup').\n"
            "- Pazi na gramatičku ispravnost: pravilno sklanjaj imenice, glagole i "
            "pridjeve; ne miješaj padeže ni glagolska vremena.\n"
            "- Odgovaraj precizno i sažeto; ne ponavljaj pitanje korisnika.\n\n"
            "Koristi sljedeće informacije iz baze znanja kao primarni izvor:\n\n"
            f"{context}"
        ),
    }

    return [system_msg] + history + [{"role": "user", "content": query}]


def ask_ollama(messages: list[dict], stream: bool = False):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": stream,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60,
            stream=stream,
        )
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Ne mogu se spojiti na Ollamu. "
            "Provjeri je li Ollama pokrenuta: `ollama serve`"
        )
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"Ollama vraca {e.response.status_code} – provjeri je li model "
            f"'{OLLAMA_MODEL}' instaliran: `ollama pull {OLLAMA_MODEL}`"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Timeout - Ollama ne odgovara na vrijeme.")


@app.route("/")
def index():
    return render_template("index.html", model=OLLAMA_MODEL)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    query = data.get("message", "").strip()
    history = data.get("history", [])

    if not query:
        return jsonify({"error": "Poruka je prazna."}), 400

    chunks = retrieve(query)
    messages = build_prompt(query, chunks, history)

    try:
        resp = ask_ollama(messages, stream=False)
        resp_json = resp.json()
        answer = resp_json["message"]["content"]
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except (KeyError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Neočekivan odgovor od Ollame: {e}"}), 500

    return jsonify({"answer": answer, "chunks": chunks})


@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json(force=True)
    query = data.get("message", "").strip()
    history = data.get("history", [])

    if not query:
        return jsonify({"error": "Poruka je prazna."}), 400

    chunks = retrieve(query)
    messages = build_prompt(query, chunks, history)

    def generate():
        yield f"data: {json.dumps({'type': 'chunks', 'chunks': chunks})}\n\n"
        try:
            resp = ask_ollama(messages, stream=True)
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    token = obj.get("message", {}).get("content", "")
                    if token:
                        yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
                    if obj.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except RuntimeError as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/retrieve", methods=["POST"])
def retrieve_only():
    data = request.get_json(force=True)
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Upit je prazan."}), 400

    chunks = retrieve(query)
    return jsonify({"query": query, "chunks": chunks})


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "model": OLLAMA_MODEL,
            "collection": COLLECTION,
            "chunks": collection.count() if collection else 0,
        }
    )


if __name__ == "__main__":
    load_resources()
    print("\nChatbot za kućnu fermentaciju pokrenut na http://localhost:3000\n")
    app.run(host="0.0.0.0", port=3000, debug=False)
