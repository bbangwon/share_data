import json
import os
import time
import uuid

from dotenv import load_dotenv
import model_utils
from langchain_neo4j import Neo4jGraph
from kiwipiepy import Kiwi
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from kiwi_bm25 import KiwiBM25

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "dragonkue/BGE-m3-ko")
INPUT_FILE = "graph_rag_inputs.json"
TERMINOLOGY_FILE = "terminology_shortcuts.json"

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_db")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "document_sections")


def main():
    print("🚀 GraphRAG Ingestion Pipeline Starting...")

    # 1. Load data
    if not os.path.exists(INPUT_FILE):
        print(
            f"❌ Error: Input file '{INPUT_FILE}' not found. Please run main.py first."
        )
        return

    print(f"📖 Loading hierarchical data from '{INPUT_FILE}'...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        sections = json.load(f)
    print(f"✅ Loaded {len(sections)} document sections.")

    # Load terminology shortcuts
    if not os.path.exists(TERMINOLOGY_FILE):
        print(f"❌ Error: Terminology file '{TERMINOLOGY_FILE}' not found.")
        return
    print(f"📖 Loading terminology shortcuts from '{TERMINOLOGY_FILE}'...")
    with open(TERMINOLOGY_FILE, "r", encoding="utf-8") as f:
        terminologies = json.load(f)
    print(f"✅ Loaded {len(terminologies)} terminology mapping entries.")

    # 2. Initialize Embeddings Model
    print(f"🧠 Initializing Embeddings model: '{EMBEDDING_MODEL_NAME}'...")
    start_time = time.time()
    embeddings_model = model_utils.get_embeddings_model(EMBEDDING_MODEL_NAME)
    print(f"✅ Embeddings model loaded in {time.time() - start_time:.2f}s")

    # 3. Flatten child chunks and prepare texts to embed
    print("✍️ Preparing child chunks for embedding...")
    flat_child_chunks = []
    texts_to_embed = []

    for sec in sections:
        title = sec.get("title", "").strip()
        for p_chunk in sec.get("parent_chunks", []):
            p_id = p_chunk["parent_chunk_id"]
            p_text = p_chunk["text"]
            for c_chunk in p_chunk.get("child_chunks", []):
                c_id = c_chunk["child_chunk_id"]
                c_text = c_chunk["text"]

                # Title + Child Text 조합하여 매칭 정확도 확장
                combined_text = f"{title}\n{c_text}".strip()

                flat_child_chunks.append(
                    {
                        "child_chunk_id": c_id,
                        "text": c_text,
                        "parent_chunk_id": p_id,
                        "parent_chunk_text": p_text,
                        "node_id": sec["node_id"],
                        "title": title,
                        "level": sec.get("level"),
                        "parent_id": sec.get("parent_id"),
                        "start_page": c_chunk.get("start_page"),
                        "parent_start_page": p_chunk.get("start_page"),
                        "section_start_page": sec.get("start_page"),
                    }
                )
                texts_to_embed.append(
                    combined_text if combined_text else "Empty Section"
                )

    total_chunks = len(flat_child_chunks)
    print(f"✍️ Generating embeddings for {total_chunks} child chunks...")

    # Batch embedding generation
    batch_size = 64
    all_embeddings = []

    start_time = time.time()
    for i in range(0, total_chunks, batch_size):
        batch_texts = texts_to_embed[i : i + batch_size]
        batch_embeddings = embeddings_model.embed_documents(batch_texts)
        all_embeddings.extend(batch_embeddings)
        print(
            f"   Processed {min(i + batch_size, total_chunks)}/{total_chunks} chunks..."
        )

    print(f"✅ Generated all embeddings in {time.time() - start_time:.2f}s")

    # Get embedding dimension
    embedding_dimension = len(all_embeddings[0])
    print(f"📏 Embedding vector dimension: {embedding_dimension}")

    # 3.5 Fit KiwiBM25 model
    print("🧠 Fitting KiwiBM25 model on child chunk texts...")
    kiwi_bm25 = KiwiBM25()
    kiwi_bm25.fit(texts_to_embed)
    bm25_model_path = "kiwi_bm25_model.json"
    kiwi_bm25.save(bm25_model_path)
    print(
        f"✅ Fitted and saved KiwiBM25 model to '{bm25_model_path}' (Vocab size: {len(kiwi_bm25.vocab)})."
    )

    # 4. Connect to Qdrant & Index vectors
    print("🔗 Connecting to Qdrant...")
    if QDRANT_URL.strip():
        qdrant_client = QdrantClient(url=QDRANT_URL)
        print(f"   Using Qdrant Server at {QDRANT_URL}")
    else:
        qdrant_client = QdrantClient(path=QDRANT_PATH)
        print(f"   Using Local Qdrant DB at '{QDRANT_PATH}'")

    print(f"📦 Recreating Qdrant collection '{QDRANT_COLLECTION_NAME}'...")
    if qdrant_client.collection_exists(collection_name=QDRANT_COLLECTION_NAME):
        qdrant_client.delete_collection(collection_name=QDRANT_COLLECTION_NAME)

    qdrant_client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config={
            "": VectorParams(size=embedding_dimension, distance=Distance.COSINE)
        },
        sparse_vectors_config={
            "text-sparse": SparseVectorParams(
                index=SparseIndexParams(
                    on_disk=True,
                )
            )
        },
    )

    print("📥 Ingesting child chunks and embeddings into Qdrant...")
    points = []
    for idx, chunk in enumerate(flat_child_chunks):
        c_id = chunk["child_chunk_id"]
        # Generate a deterministic UUID based on child_chunk_id to prevent duplicates on re-runs
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, c_id))

        # Generate BM25 sparse vector
        c_text = chunk["text"]
        title = chunk["title"]
        combined_text = f"{title}\n{c_text}".strip()
        sparse_indices, sparse_values = kiwi_bm25.get_document_vector(combined_text)

        points.append(
            PointStruct(
                id=point_id,
                vector={
                    "": all_embeddings[idx],
                    "text-sparse": SparseVector(
                        indices=sparse_indices, values=sparse_values
                    ),
                },
                payload={
                    "child_chunk_id": c_id,
                    "text": chunk["text"],
                    "body_content": chunk["text"],
                    "parent_chunk_id": chunk["parent_chunk_id"],
                    "parent_chunk_text": chunk["parent_chunk_text"],
                    "node_id": chunk["node_id"],
                    "title": chunk["title"],
                    "level": chunk["level"],
                    "parent_id": chunk["parent_id"],
                    "start_page": chunk["start_page"],
                    "parent_start_page": chunk.get("parent_start_page"),
                    "section_start_page": chunk.get("section_start_page"),
                },
            )
        )

    # Ingest in Qdrant in batches
    q_batch_size = 500
    for i in range(0, len(points), q_batch_size):
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME, points=points[i : i + q_batch_size]
        )
    print(f"✅ Ingested {len(points)} vectors into Qdrant.")

    # 5. Connect to Neo4j
    print(f"🔗 Connecting to Neo4j at {NEO4J_URI}...")
    try:
        graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            refresh_schema=False,
        )
        print("✅ Successfully connected to Neo4j!")
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        print(
            "💡 Please check your credentials in the .env file and ensure Neo4j is running."
        )
        return

    # Clear database
    print(
        "🧹 Cleaning existing DocumentSection, ParentChunk, ChildChunk, Terminology, and Synonym nodes in Neo4j..."
    )
    graph.query("MATCH (n:DocumentSection) DETACH DELETE n")
    graph.query("MATCH (n:ParentChunk) DETACH DELETE n")
    graph.query("MATCH (n:ChildChunk) DETACH DELETE n")
    graph.query("MATCH (n:Terminology) DETACH DELETE n")
    graph.query("MATCH (n:Synonym) DETACH DELETE n")

    # Drop existing index if any
    try:
        graph.query("DROP INDEX document_section_embeddings IF EXISTS")
    except Exception as e:
        print(f"ℹ️ (Optional index drop info): {e}")

    # Create unique constraints (which automatically create indexes) for lookup properties
    print("🔑 Creating unique constraints and indexes in Neo4j...")
    try:
        graph.query(
            "CREATE CONSTRAINT document_section_node_id IF NOT EXISTS FOR (s:DocumentSection) REQUIRE s.node_id IS UNIQUE"
        )
        graph.query(
            "CREATE CONSTRAINT parent_chunk_chunk_id IF NOT EXISTS FOR (p:ParentChunk) REQUIRE p.chunk_id IS UNIQUE"
        )
        graph.query(
            "CREATE CONSTRAINT child_chunk_chunk_id IF NOT EXISTS FOR (c:ChildChunk) REQUIRE c.chunk_id IS UNIQUE"
        )
        graph.query(
            "CREATE CONSTRAINT terminology_name IF NOT EXISTS FOR (t:Terminology) REQUIRE t.name IS UNIQUE"
        )
        graph.query(
            "CREATE CONSTRAINT synonym_name IF NOT EXISTS FOR (s:Synonym) REQUIRE s.name IS UNIQUE"
        )
    except Exception as e:
        print(f"ℹ️ (Constraint creation info): {e}")

    # 6. Ingest DocumentSections
    print("📥 Ingesting DocumentSections into Neo4j...")
    ingest_batch_size = 200
    for i in range(0, len(sections), ingest_batch_size):
        batch_nodes = sections[i : i + ingest_batch_size]

        # Cypher query to create nodes (without storing embeddings)
        create_nodes_query = """
        UNWIND $batch AS row
        MERGE (s:DocumentSection {node_id: row.node_id})
        SET s.title = row.title,
            s.level = toInteger(row.level),
            s.start_page = toInteger(row.start_page),
            s.body_content = row.body_content
        """
        graph.query(create_nodes_query, {"batch": batch_nodes})
        print(
            f"   Uploaded {min(i + ingest_batch_size, len(sections))}/{len(sections)} sections..."
        )

    # 7. Create parent-child relationships between DocumentSections
    print("⛓️ Constructing hierarchical relationships (PARENT_OF)...")
    create_relationships_query = """
    UNWIND $batch AS row
    WITH row WHERE row.parent_id IS NOT NULL
    MATCH (child:DocumentSection {node_id: row.node_id})
    MATCH (parent:DocumentSection {node_id: row.parent_id})
    MERGE (parent)-[:PARENT_OF]->(child)
    """
    for i in range(0, len(sections), ingest_batch_size):
        batch_nodes = sections[i : i + ingest_batch_size]
        graph.query(create_relationships_query, {"batch": batch_nodes})

    # 8. Ingest ParentChunks & ChildChunks and link them
    print("📥 Ingesting ParentChunks and ChildChunks into Neo4j...")

    parent_batch = []
    child_batch = []

    for sec in sections:
        node_id = sec["node_id"]
        for p_chunk in sec.get("parent_chunks", []):
            parent_batch.append(
                {
                    "node_id": node_id,
                    "parent_chunk_id": p_chunk["parent_chunk_id"],
                    "text": p_chunk["text"],
                    "start_page": p_chunk.get("start_page"),
                }
            )
            for c_chunk in p_chunk.get("child_chunks", []):
                child_batch.append(
                    {
                        "parent_chunk_id": p_chunk["parent_chunk_id"],
                        "child_chunk_id": c_chunk["child_chunk_id"],
                        "text": c_chunk["text"],
                        "start_page": c_chunk.get("start_page"),
                    }
                )

    # Ingest ParentChunks
    print(f"   Uploading {len(parent_batch)} ParentChunks...")
    create_parents_query = """
    UNWIND $batch AS row
    MATCH (s:DocumentSection {node_id: row.node_id})
    MERGE (p:ParentChunk {chunk_id: row.parent_chunk_id})
    SET p.text = row.text,
        p.start_page = toInteger(row.start_page)
    MERGE (s)-[:HAS_PARENT_CHUNK]->(p)
    """
    for i in range(0, len(parent_batch), ingest_batch_size):
        graph.query(
            create_parents_query, {"batch": parent_batch[i : i + ingest_batch_size]}
        )

    # Ingest ChildChunks
    print(f"   Uploading {len(child_batch)} ChildChunks...")
    create_children_query = """
    UNWIND $batch AS row
    MATCH (p:ParentChunk {chunk_id: row.parent_chunk_id})
    MERGE (c:ChildChunk {chunk_id: row.child_chunk_id})
    SET c.text = row.text,
        c.start_page = toInteger(row.start_page)
    MERGE (p)-[:HAS_CHILD_CHUNK]->(c)
    """
    for i in range(0, len(child_batch), ingest_batch_size):
        graph.query(
            create_children_query, {"batch": child_batch[i : i + ingest_batch_size]}
        )

    print("✅ Parent-Child chunks created successfully in Neo4j.")

    # 8.5 Ingest Terminology & Synonym and link to ChildChunks
    print("📥 Ingesting Terminology and Synonym nodes into Neo4j...")
    terminology_batch = []
    synonym_batch = []

    for item in terminologies:
        term = item.get("매뉴얼 상 용어", "").strip()
        if not term:
            continue
        terminology_batch.append({"name": term})

        for i in range(1, 4):
            syn = item.get(f"대체용어{i}")
            if syn and syn.strip():
                synonym_batch.append({"term_name": term, "syn_name": syn.strip()})

    # Terminology MERGE
    create_terminology_query = """
    UNWIND $batch AS row
    MERGE (t:Terminology {name: row.name})
    """
    graph.query(create_terminology_query, {"batch": terminology_batch})

    # Synonym MERGE 및 관계 생성
    create_synonym_query = """
    UNWIND $batch AS row
    MATCH (t:Terminology {name: row.term_name})
    MERGE (s:Synonym {name: row.syn_name})
    MERGE (s)-[:SYNONYM_OF]->(t)
    """
    graph.query(create_synonym_query, {"batch": synonym_batch})
    print(
        f"✅ Ingested {len(terminology_batch)} Terminology nodes and {len(synonym_batch)} Synonym nodes."
    )

    print("🧠 Analyzing ChildChunks to link Terminology nodes (MENTIONS)...")
    kiwi = Kiwi()

    # 사전의 용어/대체용어 맵 구성
    term_match_map = {}
    for item in terminologies:
        term = item.get("매뉴얼 상 용어", "").strip()
        if not term:
            continue
        match_words = {term}
        for i in range(1, 4):
            syn = item.get(f"대체용어{i}")
            if syn and syn.strip():
                match_words.add(syn.strip())
        term_match_map[term] = match_words

    mentions_batch = []

    for c in child_batch:
        c_id = c["child_chunk_id"]
        text = c["text"]

        # Kiwi 형태소 분석을 통해 명사(N) 및 외국어(SL) 추출
        noun_tokens = set()
        for token in kiwi.tokenize(text):
            if token.tag.startswith("N") or token.tag == "SL":
                noun_tokens.add(token.form)

        for term, match_words in term_match_map.items():
            matched = False
            for word in match_words:
                # 3자 이상인 단어는 단순 텍스트 포함 확인
                if len(word) >= 3 and word in text:
                    matched = True
                    break
                # 2자 이하는 명사/외국어 형태소 토큰과 정확히 일치 확인
                elif word in noun_tokens:
                    matched = True
                    break
            if matched:
                mentions_batch.append({"child_id": c_id, "term_name": term})

    # Mentions 엣지 생성 (UNWIND)
    print(
        f"🔗 Linking {len(mentions_batch)} MENTIONS relationships between ChildChunks and Terminologies..."
    )
    create_mentions_query = """
    UNWIND $batch AS row
    MATCH (c:ChildChunk {chunk_id: row.child_id})
    MATCH (t:Terminology {name: row.term_name})
    MERGE (c)-[:MENTIONS]->(t)
    """

    mentions_batch_size = 1000
    for i in range(0, len(mentions_batch), mentions_batch_size):
        graph.query(
            create_mentions_query,
            {"batch": mentions_batch[i : i + mentions_batch_size]},
        )
    print("✅ Successfully constructed MENTIONS relationships.")

    # 9. Verify database status
    verification_query = """
    RETURN count { MATCH (s:DocumentSection) } AS section_count, 
           count { MATCH (p:ParentChunk) } AS parent_count,
           count { MATCH (c:ChildChunk) } AS child_count,
           count { MATCH (t:Terminology) } AS terminology_count,
           count { MATCH (sy:Synonym) } AS synonym_count,
           count { MATCH ()-[r:PARENT_OF]->() } AS rel_parent_of,
           count { MATCH ()-[r:HAS_PARENT_CHUNK]->() } AS rel_has_parent,
           count { MATCH ()-[r:HAS_CHILD_CHUNK]->() } AS rel_has_child,
           count { MATCH ()-[r:MENTIONS]->() } AS rel_mentions
    """
    res = graph.query(verification_query)
    if res:
        print(f"\n📊 Neo4j Database Status:")
        print(f"   - Total DocumentSection Nodes: {res[0]['section_count']}")
        print(f"   - Total ParentChunk Nodes: {res[0]['parent_count']}")
        print(f"   - Total ChildChunk Nodes: {res[0]['child_count']}")
        print(f"   - Total Terminology Nodes: {res[0]['terminology_count']}")
        print(f"   - Total Synonym Nodes: {res[0]['synonym_count']}")
        print(f"   - Total PARENT_OF (Section-Section) Rel: {res[0]['rel_parent_of']}")
        print(f"   - Total HAS_PARENT_CHUNK Rel: {res[0]['rel_has_parent']}")
        print(f"   - Total HAS_CHILD_CHUNK Rel: {res[0]['rel_has_child']}")
        print(f"   - Total MENTIONS (Chunk-Terminology) Rel: {res[0]['rel_mentions']}")

    print("\n🎉 Ingestion and Indexing complete! You can now query using query.py.")


if __name__ == "__main__":
    main()
