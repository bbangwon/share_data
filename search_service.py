from __future__ import annotations

import logging
import time
from pathlib import Path
import yaml
from kiwipiepy import Kiwi
from qdrant_client import QdrantClient, models

import app.state as state
from app.config import settings
from app.models import (
    SearchRequest,
    SearchPromptResultItem,
    SearchPromptResponse,
)

logger = logging.getLogger(__name__)


def get_qdrant_client() -> QdrantClient:
    """Qdrant 클라이언트가 연결 유실되었거나 생성되지 않았을 때 재연결하여 반환합니다."""
    if state.qdrant_client is None:
        try:
            if settings.qdrant_url.strip():
                state.qdrant_client = QdrantClient(url=settings.qdrant_url)
                logger.info(f"Re-connected to Qdrant Server at {settings.qdrant_url}.")
            else:
                state.qdrant_client = QdrantClient(path=settings.qdrant_path)
                logger.info(f"Re-connected to Local Qdrant DB at {settings.qdrant_path}.")
        except Exception as e:
            logger.error(f"Qdrant Client initialization failed inside service: {e}")
            raise RuntimeError("Qdrant connection not available.") from e
    return state.qdrant_client


def extract_matched_terms(query: str, term_expansion_map: dict[str, str], kiwi: Kiwi | None) -> list[str]:
    """질문에서 용어집의 용어/대체용어와 매칭되는 단어를 추출합니다."""
    if not term_expansion_map or not kiwi:
        return []
        
    noun_tokens = set()
    try:
        for token in kiwi.tokenize(query):
            if token.tag.startswith('N') or token.tag == 'SL':
                noun_tokens.add(token.form)
    except Exception:
        pass
        
    detected_terms = set()
    for word, official_term in term_expansion_map.items():
        if len(word) >= 3 and word in query:
            detected_terms.add(official_term)
        elif word in noun_tokens:
            detected_terms.add(official_term)
            
    return list(detected_terms)


def retrieve_dense_candidates(client: QdrantClient, query_vector: list[float], limit: int) -> list:
    """Qdrant 밀집(Dense) 벡터 검색을 수행하여 후보 청크들을 가져옵니다."""
    if not query_vector:
        return []
    try:
        dense_res = client.query_points(
            collection_name=settings.qdrant_collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=0.3,
        ).points
        logger.info(f"Dense Query found {len(dense_res)} candidates.")
        return list(dense_res)
    except Exception as e:
        logger.error(f"Dense query error: {e}")
        return []


def retrieve_sparse_candidates(client: QdrantClient, query: str, limit: int) -> list:
    """Qdrant 희소(Sparse) 벡터 검색(Kiwi BM25)을 수행하여 후보 청크들을 가져옵니다."""
    try:
        if state.kiwi_bm25 is not None:
            q_indices, q_values = state.kiwi_bm25.get_query_vector(query)
        else:
            q_indices, q_values = [], []

        if q_indices and state.kiwi_bm25 is not None:
            query_sparse = models.SparseVector(indices=q_indices, values=q_values)
            sparse_res = client.query_points(
                collection_name=settings.qdrant_collection_name,
                query=query_sparse,
                using="text-sparse",
                limit=limit,
            ).points
            logger.info(f"Sparse Query found {len(sparse_res)} candidates.")
            return list(sparse_res)
    except Exception as e:
        logger.error(f"Sparse query error: {e}")
    return []


def retrieve_graph_boost_candidates(
    client: QdrantClient, 
    query_vector: list[float], 
    detected_official_terms: list[str], 
    limit: int
) -> list:
    """Neo4j 용어 검색 결과를 필터로 삼아 Qdrant에서 Graph Boost 후보 청크들을 가져옵니다."""
    if not state.graph or not detected_official_terms or not query_vector:
        return []
    try:
        cypher_boost = """
        MATCH (t:Terminology)
        WHERE t.name IN $detected_terms
        MATCH (c:ChildChunk)-[:MENTIONS]->(t)
        RETURN DISTINCT c.chunk_id AS child_chunk_id
        """
        boost_res = state.graph.query(cypher_boost, {"detected_terms": detected_official_terms})
        boost_ids = [row["child_chunk_id"] for row in boost_res if row.get("child_chunk_id")]

        if boost_ids:
            logger.info(f"Graph synonym boost matched {len(boost_ids)} chunk IDs. Querying Qdrant with filter...")
            boost_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="child_chunk_id",
                        match=models.MatchAny(any=boost_ids)
                    )
                ]
            )
            boost_res_qdrant = client.query_points(
                collection_name=settings.qdrant_collection_name,
                query=query_vector,
                query_filter=boost_filter,
                limit=limit,
                score_threshold=0.3,
            ).points
            logger.info(f"Graph synonym boost fetched {len(boost_res_qdrant)} candidate chunks from Qdrant after filtering.")
            return list(boost_res_qdrant)
    except Exception as ex:
        logger.error(f"Graph synonym boost failed: {ex}")
    return []


def merge_and_deduplicate_candidates(dense_hits: list, sparse_hits: list, graph_boost_hits: list) -> list:
    """Dense, Sparse, Graph Boost 검색 결과를 병합하고 소스 정보를 표기하며 중복을 제거합니다."""
    merged_candidates = {}
    for hit in dense_hits:
        c_id = hit.payload.get("child_chunk_id")
        if c_id:
            hit.payload["source"] = "dense"
            merged_candidates[c_id] = hit

    for hit in sparse_hits:
        c_id = hit.payload.get("child_chunk_id")
        if c_id:
            if c_id in merged_candidates:
                merged_candidates[c_id].payload["source"] = "both"
            else:
                hit.payload["source"] = "sparse"
                merged_candidates[c_id] = hit

    for hit in graph_boost_hits:
        c_id = hit.payload.get("child_chunk_id")
        if c_id:
            if c_id in merged_candidates:
                current_source = merged_candidates[c_id].payload.get("source", "")
                if "graph" not in current_source:
                    merged_candidates[c_id].payload["source"] = f"{current_source}+graph"
            else:
                hit.payload["source"] = "graph"
                merged_candidates[c_id] = hit

    return list(merged_candidates.values())


def rerank_candidates(query: str, candidates: list) -> list:
    """크로스 인코더 리랭커 모델을 사용하여 검색 후보들의 순위를 재조정합니다."""
    if not state.reranker or not candidates:
        return candidates
    try:
        pairs = [
            [
                query,
                f"{hit.payload.get('title', '')}\n{hit.payload.get('text', '')}".strip(),
            ]
            for hit in candidates
        ]
        rerank_scores = state.reranker.predict(pairs, batch_size=16)
        for hit, r_score in zip(candidates, rerank_scores):
            hit.score = float(r_score)
        return sorted(candidates, key=lambda x: x.score, reverse=True)
    except Exception as e:
        logger.error(f"Reranking execution failed: {e}")
        return candidates


def retrieve_hierarchy_info(search_results: list, limit: int) -> list:
    """Neo4j 데이터베이스로부터 매칭된 자식 청크들의 부모, 형제, 자식 노드 등의 계층 정보를 조회합니다."""
    search_results = search_results[:limit]
    child_ids = [hit.payload["child_chunk_id"] for hit in search_results if "child_chunk_id" in hit.payload]
    scores_dict = {hit.payload["child_chunk_id"]: hit.score for hit in search_results if "child_chunk_id" in hit.payload}

    results = []
    if state.graph is not None and child_ids:
        try:
            cypher_search = """
            UNWIND $child_ids AS target_child_id
            MATCH (child:ChildChunk {chunk_id: target_child_id})
            MATCH (parent_chunk:ParentChunk)-[:HAS_CHILD_CHUNK]->(child)
            MATCH (node:DocumentSection)-[:HAS_PARENT_CHUNK]->(parent_chunk)
            OPTIONAL MATCH (parent:DocumentSection)-[:PARENT_OF]->(node)
            OPTIONAL MATCH (node)-[:PARENT_OF]->(sibling:DocumentSection)
            WITH target_child_id, node, parent, parent_chunk, sibling, child
            ORDER BY sibling.node_id ASC
            RETURN 
                target_child_id AS child_chunk_id,
                node.node_id AS node_id,
                node.level AS level,
                node.title AS title,
                parent_chunk.chunk_id AS parent_chunk_id,
                parent_chunk.text AS body_content,
                parent.node_id AS parent_node_id,
                parent.title AS parent_title,
                parent.body_content AS parent_body_content,
                child.start_page AS start_page,
                collect(DISTINCT {
                    node_id: sibling.node_id, 
                    title: sibling.title, 
                    body_content: sibling.body_content
                }) AS children
            """
            db_results = state.graph.query(cypher_search, {"child_ids": child_ids})
            db_results_dict = {r["child_chunk_id"]: r for r in db_results}
            seen_parents = set()
            for child_id in child_ids:
                if child_id in db_results_dict:
                    r = db_results_dict[child_id].copy()
                    p_chunk_id = r["parent_chunk_id"]
                    if p_chunk_id in seen_parents:
                        continue
                    seen_parents.add(p_chunk_id)
                    r["score"] = scores_dict[child_id]
                    results.append(r)
        except Exception as e:
            logger.error(f"Neo4j context hierarchy retrieval failed: {e}")

    # Neo4j 데이터베이스 연결 실패 혹은 결과가 빈 경우 Qdrant 페이로드 정보를 바탕으로 Fallback
    if not results:
        seen_parents = set()
        for hit in search_results:
            p = hit.payload
            p_chunk_id = p.get("parent_chunk_id")
            if not p_chunk_id:
                continue
            if p_chunk_id in seen_parents:
                continue
            seen_parents.add(p_chunk_id)
            results.append(
                {
                    "node_id": p.get("node_id"),
                    "level": p.get("level"),
                    "title": p.get("title"),
                    "body_content": p.get("parent_chunk_text", p.get("text", "")),
                    "score": hit.score,
                    "parent_node_id": p.get("parent_id"),
                    "parent_title": "상위 섹션 정보가 Neo4j 미연결로 표시되지 않습니다.",
                    "parent_body_content": "",
                    "start_page": p.get("start_page"),
                    "children": [],
                }
            )
    return results


def format_search_results(
    results: list, 
    effective_query: str, 
    duration_ms: float, 
    terminology_context: list[str] | None = None
) -> SearchPromptResponse:
    """계층 구조 검색 결과를 프롬프트용 XML 문서 포맷 및 API 응답 스펙에 맞게 가공합니다.
    
    기존 검색 결과와 함께 추출된 매뉴얼상 용어 및 동의어 정보도 문맥(context_str) 상단에 추가하여 프롬프트를 구성합니다.
    """
    prompt_result_items = []
    context_blocks = []

    for idx, res in enumerate(results):
        node_id = res.get("node_id", "")
        title = (res.get("title") or "").strip()
        body_content = (res.get("body_content") or "").strip()
        
        parent_id = res.get("parent_node_id")
        parent_title = (res.get("parent_title") or "").strip()
        parent_body = (res.get("parent_body_content") or "").strip()
        
        children = res.get("children", [])
        children = [c for c in children if c.get("node_id") is not None]
        
        start_page = res.get("start_page")

        # 텍스트 블록 포맷팅
        block = f"### [섹션 제목: {title}]\n"
        block += f"- 파일명: {settings.default_filename}\n"
        block += f"- 페이지: {start_page}\n"
        if parent_id:
            block += f"- 상위 카테고리/섹션: {parent_title}\n"
            if parent_body:
                parent_snippet = parent_body[:200] + "..." if len(parent_body) > 200 else parent_body
                block += f"  (상위 맥락: {parent_snippet})\n"
        block += f"- 본문 내용:\n{body_content}\n"

        if children:
            block += "- 관련 하위 항목:\n"
            for child in children:
                c_title = (child.get("title") or "").strip()
                c_body = (child.get("body_content") or "").strip()
                c_body_snippet = c_body[:150] + "..." if len(c_body) > 150 else c_body
                block += f"  * {c_title}: {c_body_snippet}\n"

        # XML 구조 파싱
        page_list = [int(start_page)] if start_page is not None else []
        item_id = res.get("child_chunk_id") or f"chunk:{node_id}:{idx}"

        result_item = SearchPromptResultItem(
            rank=idx + 1,
            id=item_id,
            filename=settings.default_filename,
            page=page_list,
            context_text=block.strip(),
        )
        prompt_result_items.append(result_item)
        context_blocks.append(result_item.context_text)

    context_str = "\n\n".join(context_blocks)
    if terminology_context:
        term_block = "### [매뉴얼 용어 및 동의어 정보]\n" + "\n".join(terminology_context)
        context_str = term_block + "\n\n" + context_str
    
    # app/prompts/answer_graph_generation.yaml에서 프롬프트 템플릿 로드
    prompt_file_path = Path(__file__).parent.parent / "prompts" / "answer_graph_generation.yaml"
    empty_prompt = "참고자료를 바탕으로 사용자 질문에 답하세요.\n\n{context}\n\n사용자 질문: {query}"
    
    try:
        if prompt_file_path.exists():
            with open(prompt_file_path, "r", encoding="utf-8") as f:
                prompt_data = yaml.safe_load(f)
                if isinstance(prompt_data, dict) and "template" in prompt_data:
                    empty_prompt = prompt_data["template"]
                else:
                    logger.warning("YAML prompt template file is missing 'template' key. Using default fallback prompt.")
        else:
            logger.warning(f"YAML prompt template file not found at {prompt_file_path}. Using default fallback prompt.")
    except Exception as e:
        logger.error(f"Failed to load YAML prompt template from {prompt_file_path}: {e}. Using default fallback prompt.")

    final_prompt = empty_prompt.format(context=context_str, query=effective_query)

    return SearchPromptResponse(
        query=effective_query,
        search_result=prompt_result_items,
        empty_prompt=empty_prompt,
        prompt=final_prompt,
        total_duration_ms=duration_ms,
    )


def run_hybrid_search(request: SearchRequest) -> SearchPromptResponse:
    """하이브리드 GraphRAG 검색 파이프라인 전체 단계를 조율하여 실행합니다."""
    logger.debug(f"run_hybrid_search input params: {request.model_dump()}")
    started_at = time.perf_counter()
    effective_query = request.effective_query()
    
    # 1. Qdrant 클라이언트 획득 (유실 시 재연결)
    client = get_qdrant_client()
    
    # 2. 파라미터 한계 설정 및 동의어 매칭 단어 추출
    limit = request.limit or settings.search_limit
    dense_limit = request.dense_limit or settings.search_dense_limit
    sparse_limit = request.sparse_limit or settings.search_sparse_limit
    graph_boost_limit = request.graph_boost_limit or settings.search_graph_boost_limit
    
    detected_official_terms = []
    if request.use_graph_boost:
        detected_official_terms = extract_matched_terms(effective_query, state.term_expansion_map, state.kiwi)
        if detected_official_terms:
            logger.info(f"🔎 Detected official manual terms: {detected_official_terms}")
        
    query_vector = []
    if state.embeddings_model is not None:
        try:
            query_vector = state.embeddings_model.embed_query(effective_query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")

    # 3. Dense, Sparse, Graph Boost 검색을 통해 후보군 조회
    dense_hits = retrieve_dense_candidates(client, query_vector, dense_limit)
    sparse_hits = retrieve_sparse_candidates(client, effective_query, sparse_limit)
    
    if request.use_graph_boost:
        graph_boost_hits = retrieve_graph_boost_candidates(
            client, query_vector, detected_official_terms, graph_boost_limit
        )
    else:
        graph_boost_hits = []
        logger.info("Graph boost is disabled. Running hybrid search only.")

    # 4. 후보군 병합 및 중복제거
    merged_candidates = merge_and_deduplicate_candidates(dense_hits, sparse_hits, graph_boost_hits)

    # 5. 크로스 인코더를 통한 Rerank 수행
    reranked_results = rerank_candidates(effective_query, merged_candidates)

    # 5.1. reasoning-selector-was를 통한 원자력 안전 분야 재채점 (Nuclear Re-scoring)
    top_n = request.reasoning_rerank_top_n or settings.reasoning_rerank_top_n
    if reranked_results and settings.reasoning_selector_was_url:
        top_candidates = reranked_results[:top_n]
        
        # SimpleChunk 스펙에 맞춰 매핑
        chunks = []
        for hit in top_candidates:
            payload = hit.payload or {}
            content = payload.get("text") or payload.get("parent_chunk_text") or ""
            filename = payload.get("file") or payload.get("filename") or settings.default_filename
            title = payload.get("title")
            
            chunks.append({
                "content": content.strip() if content else "Empty content",
                "filename": filename.strip(),
                "title": title.strip() if title else None,
                "score": float(hit.score)
            })
            
        chunk_ids = [hit.payload.get("child_chunk_id") for hit in top_candidates if hit.payload]
        logger.debug(f"Selected chunk IDs for reasoning-selector: {chunk_ids}")
            
        try:
            logger.info(f"Sending {len(chunks)} chunks to reasoning-selector-was for nuclear re-scoring.")
            import httpx
            
            url = f"{settings.reasoning_selector_was_url.rstrip('/')}/evaluate-simple-nuclear"
            eval_payload = {
                "query": effective_query,
                "chunks": chunks
            }
            logger.debug(f"Calling Reasoning-Selector-WAS: url={url}, payload={eval_payload}")
            
            # 설정된 타임아웃을 적용하여 호출 (기본값 None = 무한대기)
            with httpx.Client(timeout=settings.reasoning_selector_timeout) as client:
                resp = client.post(url, json=eval_payload)
                resp.raise_for_status()
                eval_res = resp.json()
                logger.debug(f"Reasoning-Selector-WAS response status={resp.status_code}, data={eval_res}")
                
            # 반환된 새로운 점수로 업데이트
            res_chunks = eval_res.get("chunks", [])
            for idx, res_chunk in enumerate(res_chunks):
                if idx < len(top_candidates):
                    new_score = res_chunk.get("score")
                    if new_score is not None:
                        top_candidates[idx].score = float(new_score)
                        
            # 점수 기준 다시 내림차순 정렬
            reranked_results = sorted(reranked_results, key=lambda x: x.score, reverse=True)
            logger.info("Successfully re-scored and re-sorted search candidates.")
        except Exception as e:
            logger.error(f"Failed to run nuclear re-scoring via reasoning-selector-was: {e}. Fallback to original scores.")

    # 6. Neo4j 계층 구조 매칭 정보 조회
    retrieved_hierarchy = retrieve_hierarchy_info(reranked_results, limit)

    # 6.1. 동의어 및 매뉴얼 용어 정보 조회 (Synonym and Terminology retrieval)
    terminology_context = []
    if request.use_graph_boost and detected_official_terms and state.graph is not None:
        try:
            cypher_synonyms = """
            MATCH (t:Terminology)
            WHERE t.name IN $detected_terms
            OPTIONAL MATCH (s:Synonym)-[:SYNONYM_OF]->(t)
            RETURN t.name AS term_name, collect(s.name) AS synonyms
            """
            syns_res = state.graph.query(cypher_synonyms, {"detected_terms": detected_official_terms})
            for row in syns_res:
                term_name = row.get("term_name")
                syns_list = row.get("synonyms", [])
                if term_name:
                    # 빈 문자열이나 None 제거 및 공백 트림
                    syns_list = [s.strip() for s in syns_list if s and s.strip()]
                    if syns_list:
                        syns_str = ", ".join(syns_list)
                        terminology_context.append(f"- 매뉴얼 용어: {term_name} (동의어: {syns_str})")
                    else:
                        terminology_context.append(f"- 매뉴얼 용어: {term_name}")
            logger.info(f"Retrieved terminology context for {len(detected_official_terms)} terms: {terminology_context}")
        except Exception as e:
            logger.error(f"Failed to retrieve synonyms for detected terms: {e}")

    # 7. 응답 결과 최종 포맷팅
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response = format_search_results(
        retrieved_hierarchy, 
        effective_query, 
        duration_ms, 
        terminology_context=terminology_context
    )
    logger.debug(f"run_hybrid_search response: {response.model_dump()}")
    return response
