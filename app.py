import streamlit as st
import httpx
import json
import datetime
from typing import Generator

# Streamlit 페이지 설정
st.set_page_config(
    page_title="부산 AI RAG 챗봇 테스터",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 프리미엄 CSS 스타일링
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

/* 글로벌 폰트 적용 */
html, body, [class*="css"] {
    font-family: 'Outfit', 'Noto Sans KR', sans-serif;
}

/* 그라데이션 타이틀 컨테이너 */
.title-container {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 2.5rem;
    border-radius: 16px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(30, 60, 114, 0.2);
    text-align: center;
}

.title-container h1 {
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}

.title-container p {
    font-size: 1.1rem;
    font-weight: 300;
    margin-top: 0.5rem;
    opacity: 0.9;
}

/* 메트릭 카드 스타일링 */
.metric-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.dark .metric-card {
    background: #1e293b;
    border: 1px solid #334155;
}

/* RAG 참조 문서 카드 스타일링 */
.ref-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 5px solid #3b82f6;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.ref-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.05);
}

.dark .ref-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-left: 5px solid #60a5fa;
}

.ref-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}

.ref-title {
    font-weight: 600;
    font-size: 1rem;
    color: #1e293b;
}

.dark .ref-title {
    color: #f1f5f9;
}

.ref-badge {
    background: #eff6ff;
    color: #1d4ed8;
    padding: 0.2rem 0.6rem;
    font-size: 0.75rem;
    border-radius: 20px;
    font-weight: 600;
}

.dark .ref-badge {
    background: #1e3a8a;
    color: #93c5fd;
}

.ref-text {
    font-size: 0.9rem;
    color: #475569;
    line-height: 1.5;
    background: #f8fafc;
    padding: 0.8rem;
    border-radius: 6px;
}

.dark .ref-text {
    color: #cbd5e1;
    background: #0f172a;
}
</style>
""", unsafe_allow_html=True)

# 메인 타이틀 영역
st.markdown("""
<div class="title-container">
    <h1>🤖 부산 AI RAG 챗봇 테스터</h1>
    <p>Graph-WAS 하이브리드 검색 & LLM-Studio-API-Tester 연동 시뮬레이션 인터페이스</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정 영역 레이아웃
st.sidebar.image("https://img.icons8.com/nolan/96/bot.png", width=70)
st.sidebar.markdown("### ⚙️ 시스템 설정")

graph_was_url = st.sidebar.text_input(
    "🔗 Graph-WAS 주소", 
    value="http://99.1.82.168:38080",
    help="구동 중인 graph-was 서버 주소"
)

api_tester_url = st.sidebar.text_input(
    "🔗 API 테스터 주소", 
    value="http://99.1.82.207:8080",
    help="구동 중인 llm-studio-api-tester 서버 주소"
)

mode = st.sidebar.selectbox(
    "🎯 LLM 스튜디오 실행 모드", 
    options=["real", "mock"], 
    format_func=lambda x: "실제 호출 (real)" if x == "real" else "가상 응답 (mock)",
    index=0,
    help="실제 LLM Studio API를 호출할지 또는 미리 정의된 모의 답변을 사용할지 선택합니다."
)

stream_enabled = st.sidebar.checkbox(
    "🌊 SSE 스트리밍 사용", 
    value=True,
    help="상위 LLM으로부터 스트리밍 실시간 응답을 받습니다."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 세션 제어")

# 채팅 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_search_info" not in st.session_state:
    st.session_state.last_search_info = None

# 대화 기록 초기화 버튼
if st.sidebar.button("🗑️ 대화 기록 초기화", use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_search_info = None
    st.rerun()

# 레이아웃 구성: 메인 챗봇 영역과 우측 개발자 검사 콘솔
col_chat, col_dev = st.columns([2, 1])

# 왼쪽 열: 대화방 인터페이스
with col_chat:
    st.markdown("### 💬 대화방")
    
    # 기존 대화 메시지 렌더링
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # 어시스턴트 말풍선에 RAG 상세 정보가 포함되어 있는 경우 아코디언으로 표시
            if msg["role"] == "assistant" and "search_result" in msg and msg["search_result"]:
                with st.expander("🔍 RAG 검색 출처 및 프롬프트 컨텍스트", expanded=False):
                    st.markdown(f"**⏱️ 검색 소요 시간:** `{msg.get('duration_ms', 0):.2f} ms`")
                    st.markdown("#### 📚 참조된 문서 청크:")
                    for idx, doc in enumerate(msg["search_result"]):
                        pages = ", ".join(map(str, doc.get("page", [])))
                        st.markdown(f"""
                        <div class="ref-card">
                            <div class="ref-card-header">
                                <span class="ref-title">[{idx+1}] {doc.get('filename', '알 수 없는 출처')}</span>
                                <span class="ref-badge">{pages if pages else 'N/A'} 페이지</span>
                            </div>
                            <div class="ref-text">{doc.get('context_text', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if "prompt" in msg and msg["prompt"]:
                        st.markdown("#### 📝 LLM에 전송된 원본 프롬프트 페이로드:")
                        st.code(msg["prompt"], language="markdown")

    # 채팅 입력창
    if user_query := st.chat_input("원전 안전 현장조치 행동 매뉴얼 등에 대해 질문해 보세요..."):
        # 1. 사용자 질문을 렌더링하고 세션에 추가
        st.chat_message("user").markdown(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # 어시스턴트 응답 표시부 초기화
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            answer_placeholder = st.empty()
            
            # 1단계: Graph-WAS 하이브리드 검색 및 프롬프트 구성 요청
            status_placeholder.info("🔍 Graph-WAS에서 관련 문서를 검색하고 RAG 프롬프트를 구성하는 중...")
            
            search_result = []
            final_prompt = ""
            total_duration_ms = 0.0
            
            try:
                with httpx.Client(timeout=15.0) as client:
                    search_response = client.post(
                        f"{graph_was_url}/search",
                        json={"query": user_query}
                    )
                    search_response.raise_for_status()
                    search_data = search_response.json()

                    print(search_data)
                    
                    search_result = search_data.get("search_result", [])
                    final_prompt = search_data.get("prompt", "")
                    total_duration_ms = search_data.get("total_duration_ms", 0.0)
                    
                    # 개발자 검사용 세션 변수에 저장
                    st.session_state.last_search_info = {
                        "query": user_query,
                        "search_result": search_result,
                        "prompt": final_prompt,
                        "duration_ms": total_duration_ms
                    }
                    
            except Exception as e:
                status_placeholder.error(f"❌ Graph-WAS 검색 엔드포인트 연결 실패: {e}")
                # 실패 시 빈 결과를 기반으로 진행
                search_result = []
                final_prompt = user_query
                total_duration_ms = 0.0
            
            # 2단계: LLM-Studio-API-Tester를 통해 최종 답변 생성
            status_placeholder.info("⚡ LLM-Studio-API-Tester를 통해 답변 생성 중...")
            
            # ProxyRequest 규격 구성
            dialog_history = []
            # 이전 대화 이력 맵핑 (현재 턴의 사용자 질문 제외)
            for m in st.session_state.messages[:-1]:
                if m["role"] in ["user", "assistant"]:
                    dialog_history.append({"role": m["role"], "content": m["content"]})
            
            # 검색 결과를 API Tester 규격에 맞춰 맵핑 (id, passage)
            rag_psgs = []
            for doc in search_result:
                rag_psgs.append({
                    "id": doc.get("id") or "",
                    "passage": doc.get("context_text") or ""
                })
            
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            prompt = search_data.get('prompt')
            proxy_payload = {
                "user_query": prompt,
                "datetime": current_time,
                "stream": stream_enabled,
                "dialog_history": dialog_history,
                "is_rag": True if rag_psgs else False,
                "rag_psgs": rag_psgs
            }

            final_answer = ""
            
            try:
                if stream_enabled:
                    # SSE 스트림 파싱용 제너레이터 함수 정의
                    def stream_response_generator() -> Generator[str, None, None]:
                        # HTTPX 스트리밍 포스트 수행
                        with httpx.stream(
                            "POST", 
                            f"{api_tester_url}/llm-studio/v1/api/task/generate/syncapi/busan_ai_llm/nuclear_safety", 
                            json=proxy_payload, 
                            timeout=60.0
                        ) as r:
                            r.raise_for_status()
                            for line in r.iter_lines():
                                if not line:
                                    continue
                                if line.startswith("data:"):
                                    data_str = line[len("data:"):].strip()
                                    try:
                                        data_json = json.loads(data_str)
                                        # 커스텀 에러 감지
                                        if data_json.get("response_code") and data_json.get("response_code") != "C20000":
                                            err_msg = data_json.get("response_message") or "알 수 없는 상위 서버 오류"
                                            yield f"\n\n🚨 *상위 서버 오류:* {err_msg}"
                                            break
                                        
                                        chunk = data_json.get("llm_result", {}).get("answer", "")
                                        if chunk:
                                            yield chunk
                                    except Exception:
                                        pass
                                        
                    # Streamlit 실시간 스트리밍 출력 적용
                    status_placeholder.empty()
                    final_answer = answer_placeholder.write_stream(stream_response_generator())
                else:
                    # 비스트리밍 단일 응답 요청
                    with httpx.Client(timeout=60.0) as client:
                        response = client.post(
                            f"{api_tester_url}/api/llm/qa-response", 
                            json=proxy_payload
                        )
                        response.raise_for_status()
                        res_json = response.json()
                        
                        # 응답 코드 검증
                        if res_json.get("response_code") and res_json.get("response_code") != "C20000":
                            err_msg = res_json.get("response_message") or "알 수 없는 에러 코드"
                            final_answer = f"🚨 *상위 서버 오류:* {err_msg}"
                        else:
                            final_answer = res_json.get("llm_result", {}).get("answer", "")
                        
                        status_placeholder.empty()
                        answer_placeholder.markdown(final_answer)
                
            except Exception as e:
                status_placeholder.empty()
                final_answer = f"⚠️ *LLM Studio API 통신 오류 발생:* {e}"
                answer_placeholder.markdown(final_answer)
            
            # 최종 응답 및 RAG 메타데이터를 세션 대화 로그에 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_answer,
                "search_result": search_result,
                "prompt": final_prompt,
                "duration_ms": total_duration_ms
            })
            
            # 답변 아래에 참조 문서 정보 렌더링
            if search_result:
                with st.expander("🔍 RAG 검색 출처 및 프롬프트 컨텍스트", expanded=False):
                    st.markdown(f"**⏱️ 검색 소요 시간:** `{total_duration_ms:.2f} ms`")
                    st.markdown("#### 📚 참조된 문서 청크:")
                    for idx, doc in enumerate(search_result):
                        pages = ", ".join(map(str, doc.get("page", [])))
                        st.markdown(f"""
                        <div class="ref-card">
                            <div class="ref-card-header">
                                <span class="ref-title">[{idx+1}] {doc.get('filename', '알 수 없는 출처')}</span>
                                <span class="ref-badge">{pages if pages else 'N/A'} 페이지</span>
                            </div>
                            <div class="ref-text">{doc.get('context_text', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if final_prompt:
                        st.markdown("#### 📝 LLM에 전송된 원본 프롬프트 페이로드:")
                        st.code(final_prompt, language="markdown")

# 오른쪽 열: 개발자 콘솔 및 실시간 RAG 검사기
with col_dev:
    st.markdown("### 🛠️ 개발자 검사기")
    
    if st.session_state.last_search_info:
        info = st.session_state.last_search_info
        st.success("✅ 최신 검색 트랜잭션 로드됨")
        
        # 소요 시간 및 매칭 건수 요약 메트릭
        st.markdown(f"""
        <div class="metric-card">
            <small style="color: #64748b;">Graph-WAS 검색 소요 시간</small>
            <h3 style="color: #3b82f6; margin: 0; font-size: 1.8rem;">{info['duration_ms']:.2f} ms</h3>
            <small style="color: #64748b;">참조 문서 조각: <b>{len(info['search_result'])}</b>개</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 시스템 프롬프트 확인
        st.markdown("#### 📝 완성된 시스템 프롬프트")
        st.text_area(
            "Graph-WAS에서 빌드된 원본 프롬프트:", 
            value=info["prompt"], 
            height=250,
            disabled=True
        )
        
        # 원본 JSON 출력
        st.markdown("#### 📦 원본 검색결과 JSON")
        st.json(info["search_result"])
    else:
        st.info("💡 질문을 입력하면 여기에 실시간 검색 트랜잭션 정보가 표시됩니다.")
