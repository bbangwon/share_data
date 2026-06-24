import argparse
import json
import os
import time

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def parse_goldenset_pages(pages_str):
    if not pages_str:
        return set()
    pages = set()
    for part in str(pages_str).split(","):
        part = part.strip()
        if not part:
            continue
        try:
            pages.add(int(part))
        except ValueError:
            pages.add(part)
    return pages


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate LLM Reasoning Selector Rerank via WAS API."
    )
    parser.add_argument(
        "--limit-queries",
        type=int,
        default=None,
        help="Limit number of queries to evaluate (for testing)",
    )
    parser.add_argument(
        "--was-url",
        type=str,
        default="http://localhost:8000",
        help="Reasoning Selector WAS URL",
    )
    args = parser.parse_args()

    print("--------------------------------------------------")
    print(f"🤖 LLM Reasoning Selector Evaluation (WAS API Batch)")
    print(f"   WAS URL      : {args.was_url}")
    print(f"   Limit Queries: {args.limit_queries}")
    print("--------------------------------------------------")

    input_path = "/Users/youngilchung/study/graph_test/goldenset_qdrant_similarity_and_rerank_results_refined.json"
    output_path = "/Users/youngilchung/study/graph_test/goldenset_qdrant_similarity_and_rerank_results_reasoning_selector.json"

    print("📖 Loading original results...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.limit_queries:
        data = data[: args.limit_queries]

    total_queries = len(data)
    original_top20_hits = 0
    original_top5_hits = 0
    llm_top5_hits = 0

    reranked_data = []

    for idx, item in enumerate(data):
        query = item.get("질의문")
        correct_pages = parse_goldenset_pages(
            ",".join(map(str, item.get("정답 쪽번호", [])))
        )
        retrieved_pages = item.get("쪽번호", [])
        titles = item.get("타이틀", [])
        chunks = item.get("청크", [])
        node_ids = item.get("노드 ID", [])
        original_scores = item.get("유사도 점수", [])
        rerank_scores = item.get("rerank 점수", [])

        # Handle single values
        if isinstance(retrieved_pages, (int, str)):
            retrieved_pages = [retrieved_pages]
        if isinstance(titles, str):
            titles = [titles]
        if isinstance(chunks, str):
            chunks = [chunks]
        if isinstance(node_ids, str):
            node_ids = [node_ids]
        if isinstance(original_scores, (int, float)):
            original_scores = [original_scores]
        if isinstance(rerank_scores, (int, float)):
            rerank_scores = [rerank_scores]

        # Ensure lists are aligned
        n_candidates = min(len(retrieved_pages), len(titles), len(chunks), 20)

        # Check original hits
        orig_top20_retrieved = retrieved_pages[:20]
        orig_top5_retrieved = retrieved_pages[:5]
        has_orig_top20 = any(p in correct_pages for p in orig_top20_retrieved)
        has_orig_top5 = any(p in correct_pages for p in orig_top5_retrieved)

        if has_orig_top20:
            original_top20_hits += 1
        if has_orig_top5:
            original_top5_hits += 1

        print(f"\n[{idx + 1}/{total_queries}] Query: '{query}'")
        print(f"   Correct Pages: {list(correct_pages)}")
        print(
            f"   Original Top 20 Hit: {has_orig_top20} | Original Top 5 Hit: {has_orig_top5}"
        )

        candidate_llm_scores = []
        candidate_reasons = []

        query_t0 = time.time()

        # Build API chunks payload
        api_chunks = []
        for i in range(n_candidates):
            title = titles[i] if i < len(titles) else "N/A"
            body = chunks[i] if i < len(chunks) else "N/A"
            r_score = rerank_scores[i] if i < len(rerank_scores) else 0.0

            api_chunks.append(
                {
                    "content": body,
                    "filename": "(사회재난-17) 2025-2차 원전안전 분야(방사능 누출) 현장조치 행동 매뉴얼(4차 개정 251013).pdf",
                    "title": title,
                    "score": float(r_score),
                }
            )

        payload = {"query": query, "chunks": api_chunks}

        try:
            # Request to WAS API (evaluate-simple-nuclear)
            response = requests.post(
                f"{args.was_url}/evaluate-simple-nuclear", json=payload, timeout=60
            )
            response.raise_for_status()
            res_data = response.json()

            returned_chunks = res_data.get("chunks", [])
            for i in range(n_candidates):
                score = 0.0
                reason = "API 기반 평가 (Reasoning 미지원)"
                if i < len(returned_chunks):
                    score = float(returned_chunks[i].get("score", 0.0))
                else:
                    # Fallback if returned chunk size mismatches
                    score = float(1.0 / (i + 1))
                candidate_llm_scores.append(score)
                candidate_reasons.append(reason)
        except Exception as e:
            # Fallback on failure
            print(f"   ⚠️ API 호출 실패: {e}. Fallback 점수 적용.")
            for i in range(n_candidates):
                score = float(1.0 / (i + 1))
                reason = f"Error during API evaluation: {e}"
                candidate_llm_scores.append(score)
                candidate_reasons.append(reason)

        # Print batch completion log
        first_chunk_score = candidate_llm_scores[0] if candidate_llm_scores else 0.0
        print(
            f"   [API Batch Evaluation] Chunks Scored: {n_candidates} | First Score: {first_chunk_score:.4f} | Latency: {time.time() - query_t0:.2f}s"
        )

        # zip all information together to sort them by LLM score descending
        candidates_info = []
        for i in range(n_candidates):
            candidates_info.append(
                {
                    "node_id": node_ids[i] if i < len(node_ids) else "N/A",
                    "title": titles[i] if i < len(titles) else "N/A",
                    "page": retrieved_pages[i] if i < len(retrieved_pages) else "N/A",
                    "chunk": chunks[i] if i < len(chunks) else "N/A",
                    "original_score": original_scores[i]
                    if i < len(original_scores)
                    else 0.0,
                    "rerank_score": rerank_scores[i] if i < len(rerank_scores) else 0.0,
                    "llm_score": candidate_llm_scores[i],
                    "llm_reason": candidate_reasons[i],
                }
            )

        # Sort candidates: primarily by llm_score desc, secondarily by original rerank_score desc
        candidates_info.sort(
            key=lambda x: (x["llm_score"], x["rerank_score"]), reverse=True
        )

        # Check hit on new Top 5
        new_top5_pages = [c["page"] for c in candidates_info[:5]]
        has_llm_top5 = any(p in correct_pages for p in new_top5_pages)
        if has_llm_top5:
            llm_top5_hits += 1

        print(f"   New Top 5 Pages: {new_top5_pages}")
        print(
            f"   New Top 5 Hit: {has_llm_top5} "
            + (
                "✅ IMPROVED!"
                if (has_llm_top5 and not has_orig_top5)
                else (
                    "❌ DEGRADED!"
                    if (not has_llm_top5 and has_orig_top5)
                    else "➖ UNCHANGED"
                )
            )
        )

        # Store result
        reranked_data.append(
            {
                "질의문": query,
                "정답 쪽번호": list(correct_pages),
                "Original Top 20 Hit": has_orig_top20,
                "Original Top 5 Hit": has_orig_top5,
                "LLM Top 5 Hit": has_llm_top5,
                "노드 ID": [c["node_id"] for c in candidates_info],
                "타이틀": [c["title"] for c in candidates_info],
                "쪽번호": [c["page"] for c in candidates_info],
                "청크": [c["chunk"] for c in candidates_info],
                "유사도 점수": [c["original_score"] for c in candidates_info],
                "rerank 점수": [c["rerank_score"] for c in candidates_info],
                "llm 점수": [c["llm_score"] for c in candidates_info],
                "llm 채점 근거": [c["llm_reason"] for c in candidates_info],
            }
        )

    # Save to file
    print(f"\n💾 Saving LLM rerank results to '{output_path}'...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reranked_data, f, ensure_ascii=False, indent=4)

    # Print summary statistics
    print("\n==================================================")
    print("🏆 RE-RANK EVALUATION SUMMARY")
    print(f"   Total Queries Evaluated: {total_queries}")
    if total_queries > 0:
        orig_top20_rate = (original_top20_hits / total_queries) * 100
        orig_top5_rate = (original_top5_hits / total_queries) * 100
        llm_top5_rate = (llm_top5_hits / total_queries) * 100
        print(
            f"   Original Top 20 Hit Rate : {original_top20_hits} / {total_queries} ({orig_top20_rate:.2f}%)"
        )
        print(
            f"   Original Top 5 Hit Rate  : {original_top5_hits} / {total_queries} ({orig_top5_rate:.2f}%)"
        )
        print(
            f"   LLM Rerank Top 5 Hit Rate: {llm_top5_hits} / {total_queries} ({llm_top5_rate:.2f}%)"
        )
        improvement = llm_top5_rate - orig_top5_rate
        print(f"   Top 5 Improvement        : {improvement:+.2f}%")
    print("==================================================")


if __name__ == "__main__":
    main()
