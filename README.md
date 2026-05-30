# Chatbot za kućnu fermentaciju – RAG pipeline (Faza 2B)

## Pregled projekta

Lokalni RAG (Retrieval-Augmented Generation) chatbot za kućnu fermentaciju.  
Koristi **Ollama** kao lokalni LLM, **ChromaDB** za vektorsku bazu podataka i **Flask** kao web sučelje.

---

## Arhitektura sustava

```
Korisnik (browser)
       |
       v
  Flask (app.py) - lokalni web server (port 3000)
       |
       +-- 1. RAG Retrieval
       |      |
       |      +-- Sentence Transformers
       |      |   (paraphrase-multilingual-MiniLM-L12-v2)
       |      +-- ChromaDB (chroma_db/)
       |
       +-- 2. LLM Generacija
              |
              +-- Ollama API (localhost:11434)
              +-- jobautomation/OpenEuroLLM-Croatian:latest
```

### Tok podataka: dokument, embedding, retrieval, odgovor

```
MD dokumenti (md/*.md)
     |
     v
ingest.py
     |
     v
Parse YAML frontmatter
     |
     v
Podjela na chunkove (~600 znakova, preklapanje 80)
     |
     v
sentence-transformers -> embedding vektori (384 dim.)
     |
     v
ChromaDB kolekcija "fermentacija" (cosine similarity)
     |
     v
Upit -> embedding -> cosine similarity pretraga -> top-4 chunkovi
     |
     v
System prompt + kontekst (top-4 chunkovi) + povijest razgovora
     |
     v
Ollama API (jobautomation/OpenEuroLLM-Croatian:latest) -> tekstualni odgovor
     |
     v
Flask JSON odgovor -> browser
```

---

## Instalacija i pokretanje

### 1. Preduvjeti

- Python 3.10+
- [Ollama](https://ollama.com) instaliran lokalno

### 2. Instaliraj ovisnosti

```bash
pip install -r requirements.txt
```

### 3. Instaliraj i pokreni Ollama

```bash
ollama serve
ollama pull jobautomation/OpenEuroLLM-Croatian:latest
```

**Odabrani model:**

| Model                                       | Kvaliteta HR odgovora | Bilješka                                     |
| ------------------------------------------- | --------------------- | -------------------------------------------- |
| `jobautomation/OpenEuroLLM-Croatian:latest` | Vrlo dobra            | Bolji hrvatski odgovori, nešto sporiji model |

> **Obrazloženje odabira OpenEuroLLM Croatian modela:**  
> `jobautomation/OpenEuroLLM-Croatian:latest` odabran je jer daje prirodnije i kvalitetnije odgovore na hrvatskom jeziku. Model je nešto sporiji od manjih općenitih modela, ali je to prihvatljivo jer je cilj projekta demonstrirati kvalitetan lokalni RAG odgovor na hrvatskom jeziku.

### 4. Ingesiraj dokumente u ChromaDB

```bash
python ingest.py
```

Očekivani ispis:

```
------------------------------------------------------------
  RAG INGEST - Chatbot za kućnu fermentaciju
------------------------------------------------------------

Učitavam dokumente iz: /path/to/md

  OK 01_domena_chatbota.md - 5 chunk(a)
  OK 02_oprema_i_higijena.md - 6 chunk(a)
  ...
  OK README_RAG.md - 4 chunk(a)

Ukupno dokumenata: 12
Vektoriziram 58 chunkova...
ChromaDB kolekcija 'fermentacija' kreirana s 58 chunkova.

Demo retrieval
Upit: Na površini kombuche pojavila se crna plijesan. Što trebam napraviti?

[Chunk 1] Sličnost: 0.8921  |  Izvor: 05_kombucha_i_fermentacija_caja.md
Naslov dokumenta: Kombucha i fermentacija čaja
...
```

### 5. Pokreni Flask aplikaciju

```bash
python app.py
```

Otvori browser: **http://localhost:3000**

---

## Korištene knjižnice i tehnologije

| Komponenta      | Tehnologija                             | Svrha                                    |
| --------------- | --------------------------------------- | ---------------------------------------- |
| LLM             | Ollama + `jobautomation/OpenEuroLLM-Croatian:latest` | Generacija odgovora na hrvatskom jeziku  |
| Embedding model | `paraphrase-multilingual-MiniLM-L12-v2` | Vektorizacija teksta (podržava HR jezik) |
| Vektorska baza  | ChromaDB (lokalno, persistentno)        | Pohrana i pretraga chunkova              |
| Web server      | Flask 3.0                               | HTTP API + HTML sučelje                  |
| Chunking        | Vlastita implementacija                 | Podjela MD dokumenata po naslovima       |
| Frontend        | HTML/CSS/JavaScript                     | Chatbot sučelje u browseru               |

---

## Konkretni primjer retrievala

**Upit:** `"Na površini kombuche pojavile su se crne mrlje i miris je jako neugodan."`

**Dohvaćeni chunkovi (top-3):**

```
[1] 05_kombucha_i_fermentacija_caja.md  (sličnost: 0.891)
    Tags: kombucha, fermentacija čaja, SCOBY, sigurnost hrane
    "Plijesan na kombuchi najčešće se pojavljuje na površini...
    Ako korisnik opisuje suhe, pahuljaste ili obojene mrlje na površini,
    osobito zelene, crne, plave, ružičaste ili narančaste, chatbot treba
    savjetovati odbacivanje cijele kulture i tekućine."

[2] 07_sigurnost_i_kvarenje.md  (sličnost: 0.847)
    Tags: sigurnost hrane, kvarenje, kontaminacija, plijesan
    "Ako korisnik opisuje ružičastu, crnu, plavu, zelenu ili narančastu
    plijesan, chatbot treba jasno preporučiti odbacivanje proizvoda."

[3] 10_primjeri_pitanja_i_odgovora.md  (sličnost: 0.823)
    Tags: pitanja, odgovori, interakcije
    "Na površini kombuche pojavile su mi se crne mrlje i miris je jako
    neugodan. Je li to normalno? — Crne mrlje i prodoran neugodan miris
    mogu upućivati na kontaminaciju..."
```

**Zašto su ovi chunkovi dohvaćeni?**  
Embedding model `paraphrase-multilingual-MiniLM-L12-v2` pretvorio je upit u vektor i pronašao semantički najsličnije dijelove baze znanja mjerenjem kosinusne sličnosti. Chunk iz dokumenta o kombuchi dobio je najvišu ocjenu jer direktno opisuje pojavu plijesni i preporuku odbacivanja za tu vrstu fermentacije. Dokument o sigurnosti hrane je semantički blizak jer sadrži iste koncepte (plijesan, kontaminacija, odbacivanje). Primjeri interakcija imaju visoku ocjenu jer sadrže gotovo identičan primjer pitanja.

---

## Struktura projekta

```
rag_chatbot/
+-- md/
|   +-- 01_domena_chatbota.md
|   +-- 02_oprema_i_higijena.md
|   +-- 03_fermentacija_povrca.md
|   +-- 04_kefir_i_mlijecna_fermentacija.md
|   +-- 05_kombucha_i_fermentacija_caja.md
|   +-- 06_kiselo_tijesto.md
|   +-- 07_sigurnost_i_kvarenje.md
|   +-- 08_vodici_po_koracima.md
|   +-- 09_pravila_odgovaranja_chatbota.md
|   +-- 10_primjeri_pitanja_i_odgovora.md
|   +-- 11_podaci_za_rag_opis.md
|   +-- README_RAG.md
+-- templates/
|   +-- index.html
+-- chroma_db/
+-- ingest.py
+-- app.py
+-- requirements.txt
+-- README.md
```

---

## API endpointi

| Metoda | Putanja     | Opis                                   |
| ------ | ----------- | -------------------------------------- |
| GET    | `/`         | Web sučelje chatbota                   |
| POST   | `/chat`     | Pošalji poruku, dobij odgovor + izvore |
| POST   | `/retrieve` | Samo retrieval (bez LLM-a), za debug   |
| GET    | `/health`   | Status servisa                         |

### POST `/chat` – primjer

```json
{
  "message": "Kako napraviti kiseli kupus?",
  "history": []
}
```

```json
{
  "answer": "Za kiseli kupus potrebni su ti...",
  "chunks": [
    {
      "text": "...",
      "filename": "03_fermentacija_povrca.md",
      "title": "Fermentacija povrća: kiseli kupus i kimchi",
      "tags": "fermentacija povrća, kiseli kupus, kimchi",
      "score": 0.8734
    }
  ]
}
```

---

## Promjena modela

U `app.py`, redak:

```python
OLLAMA_MODEL = "jobautomation/OpenEuroLLM-Croatian:latest"
```

Po potrebi se može zamijeniti drugim dostupnim Ollama modelom, ali za ovu fazu odabran je OpenEuroLLM Croatian zbog bolje kvalitete hrvatskog jezika.

---

## Autori

Robert Domgjonaj · Mihael Baivić · Matej Čiček  
Fakultet organizacije i informatike, Varaždin – 2026.
