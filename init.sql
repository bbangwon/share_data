--
-- PostgreSQL database dump
--

-- Dumped from database version 17.6 (Debian 17.6-2.pgdg13+1)
-- Dumped by pg_dump version 18.0

-- Started on 2025-12-03 15:01:54

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 217 (class 1259 OID 16385)
-- Name: TB_CHAT_HISTORY; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."TB_CHAT_HISTORY" (
    chat_session_id integer NOT NULL,
    chat_number integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    is_file_content boolean NOT NULL,
    user_message text NOT NULL,
    user_message_summary text,
    bot_message text,
    bot_message_summary text,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public."TB_CHAT_HISTORY" OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16390)
-- Name: TB_CHAT_SESSION; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."TB_CHAT_SESSION" (
    id integer NOT NULL,
    user_id character varying(50) NOT NULL,
    bot_id character varying(50) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public."TB_CHAT_SESSION" OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16393)
-- Name: TB_CHAT_SESSION_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."TB_CHAT_SESSION_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."TB_CHAT_SESSION_id_seq" OWNER TO postgres;

--
-- TOC entry 3485 (class 0 OID 0)
-- Dependencies: 219
-- Name: TB_CHAT_SESSION_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."TB_CHAT_SESSION_id_seq" OWNED BY public."TB_CHAT_SESSION".id;


--
-- TOC entry 220 (class 1259 OID 16394)
-- Name: TB_CHAT_SUMMARY; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."TB_CHAT_SUMMARY" (
    id integer NOT NULL,
    chat_session_id integer NOT NULL,
    start_number integer NOT NULL,
    end_number integer NOT NULL,
    message text NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public."TB_CHAT_SUMMARY" OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16399)
-- Name: TB_CHAT_SUMMARY_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."TB_CHAT_SUMMARY_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."TB_CHAT_SUMMARY_id_seq" OWNER TO postgres;

--
-- TOC entry 3488 (class 0 OID 0)
-- Dependencies: 221
-- Name: TB_CHAT_SUMMARY_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."TB_CHAT_SUMMARY_id_seq" OWNED BY public."TB_CHAT_SUMMARY".id;


--
-- TOC entry 222 (class 1259 OID 16400)
-- Name: TB_SETTING; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."TB_SETTING" (
    key character varying(50) NOT NULL,
    value text,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public."TB_SETTING" OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16405)
-- Name: TB_STATIC_FEEDBACK; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."TB_STATIC_FEEDBACK" (
    id integer NOT NULL,
    parent_id integer,
    message_type character varying(20) NOT NULL,
    sort_number smallint NOT NULL,
    content text,
    from_postback character varying(20),
    to_postback character varying(20),
    created_at timestamp without time zone NOT NULL,
    bot_service character varying(50)
);


ALTER TABLE public."TB_STATIC_FEEDBACK" OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16410)
-- Name: TB_STATIC_FEEDBACK_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."TB_STATIC_FEEDBACK_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."TB_STATIC_FEEDBACK_id_seq" OWNER TO postgres;

--
-- TOC entry 3492 (class 0 OID 0)
-- Dependencies: 224
-- Name: TB_STATIC_FEEDBACK_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."TB_STATIC_FEEDBACK_id_seq" OWNED BY public."TB_STATIC_FEEDBACK".id;


--
-- TOC entry 225 (class 1259 OID 17157)
-- Name: TB_STATIC_MESSAGE_FROM_INTENT; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."TB_STATIC_MESSAGE_FROM_INTENT" (
    id integer NOT NULL,
    intent_id integer NOT NULL,
    intent_name character varying(50) NOT NULL,
    message text,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public."TB_STATIC_MESSAGE_FROM_INTENT" OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 17162)
-- Name: TB_STATIC_MESSAGE_FROM_INTENT_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."TB_STATIC_MESSAGE_FROM_INTENT_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."TB_STATIC_MESSAGE_FROM_INTENT_id_seq" OWNER TO postgres;

--
-- TOC entry 3495 (class 0 OID 0)
-- Dependencies: 226
-- Name: TB_STATIC_MESSAGE_FROM_INTENT_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."TB_STATIC_MESSAGE_FROM_INTENT_id_seq" OWNED BY public."TB_STATIC_MESSAGE_FROM_INTENT".id;


--
-- TOC entry 3297 (class 2604 OID 16414)
-- Name: TB_CHAT_SESSION id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_CHAT_SESSION" ALTER COLUMN id SET DEFAULT nextval('public."TB_CHAT_SESSION_id_seq"'::regclass);


--
-- TOC entry 3298 (class 2604 OID 16415)
-- Name: TB_CHAT_SUMMARY id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_CHAT_SUMMARY" ALTER COLUMN id SET DEFAULT nextval('public."TB_CHAT_SUMMARY_id_seq"'::regclass);


--
-- TOC entry 3299 (class 2604 OID 16416)
-- Name: TB_STATIC_FEEDBACK id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_STATIC_FEEDBACK" ALTER COLUMN id SET DEFAULT nextval('public."TB_STATIC_FEEDBACK_id_seq"'::regclass);


--
-- TOC entry 3300 (class 2604 OID 17168)
-- Name: TB_STATIC_MESSAGE_FROM_INTENT id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_STATIC_MESSAGE_FROM_INTENT" ALTER COLUMN id SET DEFAULT nextval('public."TB_STATIC_MESSAGE_FROM_INTENT_id_seq"'::regclass);


--
-- TOC entry 3468 (class 0 OID 16385)
-- Dependencies: 217
-- Data for Name: TB_CHAT_HISTORY; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."TB_CHAT_HISTORY" (chat_session_id, chat_number, created_at, is_file_content, user_message, user_message_summary, bot_message, bot_message_summary, updated_at) FROM stdin;
\.


--
-- TOC entry 3469 (class 0 OID 16390)
-- Dependencies: 218
-- Data for Name: TB_CHAT_SESSION; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."TB_CHAT_SESSION" (id, user_id, bot_id, created_at) FROM stdin;
\.


--
-- TOC entry 3471 (class 0 OID 16394)
-- Dependencies: 220
-- Data for Name: TB_CHAT_SUMMARY; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."TB_CHAT_SUMMARY" (id, chat_session_id, start_number, end_number, message, created_at) FROM stdin;
\.


--
-- TOC entry 3473 (class 0 OID 16400)
-- Dependencies: 222
-- Data for Name: TB_SETTING; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."TB_SETTING" (key, value, created_at) FROM stdin;
app_name	AI부기주무관	2025-10-12 04:34:58.022219
version	0.0.1	2025-10-12 04:34:58.022219
\.


--
-- TOC entry 3474 (class 0 OID 16405)
-- Dependencies: 223
-- Data for Name: TB_STATIC_FEEDBACK; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."TB_STATIC_FEEDBACK" (id, parent_id, message_type, sort_number, content, from_postback, to_postback, created_at, bot_service) FROM stdin;
1	\N	text	1	안녕하세요. AI맞춤 행정업무를 지원하는 AI 부기주무관 입니다. 업무에 궁금한 점을 바로 질문하시거나 아래에서 해당하는 질문을 클릭해주세요.	start_service	\N	2025-09-10 15:06:46.548392	\N
2	\N	main_carousel	2	{"alt_text": "AI 부기주무관이 지원 업무/자주묻는 질문"}	start_service	\N	2025-09-10 15:06:46.548392	\N
5	3	message	1	{"label": "업무 영역", "text": "AI 부기주무관 지원 업무 영역"}	\N	task_area	2025-09-10 15:06:46.548392	\N
7	4	message	1	{"label": "FAQ", "text": "FAQ"}	\N	faq	2025-09-10 15:06:46.548392	\N
8	4	message	2	{"label": "나의 최근 질문", "text": "나의 최근 질문"}	\N	recent_questions	2025-09-10 15:06:46.548392	\N
9	\N	text	1	업무영역을 선택하셨군요! AI 부기주무관이 지원하는 업무 구분은 아래와 같습니다. 해당하는 업무를 클릭하면 상세한 설명을 보실 수 있습니다.	task_area	\N	2025-09-10 15:06:46.548392	\N
10	\N	button_template	2	{"alt_text": "AI 부기주무관 지원 업무"}	task_area	\N	2025-09-10 15:06:46.548392	\N
11	10	message	1	{"label": "시민서비스", "text": "시민서비스"}	\N	citizen_service	2025-09-10 15:06:46.548392	\N
12	10	message	1	{"label": "예산회계", "text": "예산회계"}	\N	budget_accounting	2025-09-10 15:06:46.548392	\N
13	10	message	1	{"label": "문서봇", "text": "문서봇"}	\N	document_bot	2025-09-10 15:06:46.548392	\N
14	10	message	1	{"label": "법무∙특사경", "text": "법무∙특사경"}	\N	law	2025-09-10 15:06:46.548392	\N
15	10	message	1	{"label": "인사∙복지∙교육", "text": "인사∙복지∙교육"}	\N	employee_welfare	2025-09-10 15:06:46.548392	\N
16	10	message	1	{"label": "IT & 빅데이터", "text": "IT & 빅데이터"}	\N	it_bigdata	2025-09-10 15:06:46.548392	\N
17	10	message	1	{"label": "홍보", "text": "홍보"}	\N	promotion	2025-09-10 15:06:46.548392	\N
18	10	message	1	{"label": "기록물", "text": "기록물"}	\N	record	2025-09-10 15:06:46.548392	\N
19	10	message	1	{"label": "대외협력", "text": "대외협력"}	\N	external_cooper	2025-09-10 15:06:46.548392	\N
20	10	message	1	{"label": "안전∙환경", "text": "안전∙환경"}	\N	safety_environment	2025-09-10 15:06:46.548392	\N
21	\N	text	1	최근 부기주무관에 문의한 질문 내역을 확인할 수 있습니다.	recent_questions	\N	2025-09-10 15:06:46.594016	\N
22	\N	button_carousel	2	{"alt_text": "나의 최근 질문"}	recent_questions	\N	2025-09-10 15:06:46.594016	\N
23	22	button	1	{"text": "나의 최근 질문"}	\N	\N	2025-09-10 15:06:46.594016	\N
24	23	message	1	{"text": "나의 최근 질문", "label": "답변보기"}	\N	\N	2025-09-10 15:06:46.594016	\N
25	\N	text	1	시민서비스를 선택하셨군요! 시민서비스는 부산시정, 당직민원, 청사안내 업무를 지원합니다.\n\n부산시정 업무에서는 시정, 시장, 정책, 시민, 부산, 경영관리계획, 기본계획, 중장기, 업무계획, 의전 등의 업무를 지원합니다.\n\n당직민원 업무에서는 민원, 전화 문의, 질문과 답변 업무를 지원합니다.\n\n청사안내 업무에서는 청사, 층별, 부서안내, 건물, 주차, 방문자, 안내 업무를 지원합니다.\n\n시민서비스에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 악성민원 응대 및 대응관련 매뉴얼 알려주세요.	citizen_service	\N	2025-09-10 15:06:46.599071	\N
4	2	carousel_column	2	{"image_url": "https://busanai.busan.go.kr/views/assets/images/c2.png", "text": "AI 부기주무관에 자주묻는 질문을 확인해보세요."}	\N	\N	2025-09-10 15:06:46.548392	\N
27	\N	text	1	문서봇을 선택하셨군요! 문서봇 업무에서는 문서작성 등의 업무를 지원합니다.\n\n문서작성 업무에서는 인사말씀, 보도자료, 계획서, 보고자료등 초안생성 업무를 지원합니다.\n\n문서작성에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 원자력 안전 및 방사능방지 대책 추진 유공자 표창식 행사와 관련하여 시장님의 인사말씀 초안을 작성해주세요	document_bot	\N	2025-09-10 15:06:46.599071	\N
28	\N	text	1	법무∙특사경을 선택하셨군요! 법무∙특사경 업무에서는 법령, 사법경찰 등의 업무를 지원합니다.\n\n법령 업무에서는 법령, 법률, 조례, 규칙, 시행령, 시행규칙, 규정, 법무, 입법 등의 업무를 지원합니다.\n\n사법경찰 업무에서는 사법경찰, 특사경, 단속, 수사 등의 업무를 지원합니다.\n\n법무∙특사경에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 부산시 조례 제정 절차는 어떻게 되나요?	law	\N	2025-09-10 15:06:46.599071	\N
29	\N	text	1	인사∙복지∙교육을 선택하셨군요! 인사∙복지∙교육 업무에서는 직원복지, 교육 등의 업무를 지원합니다.\n\n직원복지 업무에서는 복지, 연가, 건강검진, 출장비, 식당, 휴가, 인사, 채용 등의 업무를 지원합니다.\n\n교육 업무에서는 교육, 훈련, 연수, 인력개발, 직무교육, 시민교육, 강의, 학습, 역량, 개발원 등의 업무를 지원합니다.\n\n인사∙복지∙교육에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 모범공무원 표창은 누구에게 주어지나요?	employee_welfare	\N	2025-09-10 15:06:46.599071	\N
30	\N	text	1	IT & 빅데이터를 선택하셨군요! IT & 빅데이터 업무에서는 IT, 정보보안, 빅데이터 등의 업무를 지원합니다.\n\nIT 업무에서는 시스템, DRM, PC, 권한, 장애, 전산, 정보통신, 보안, IP, 행정전화 등의 업무를 지원합니다.\n\n정보보안 업무에서는 보안, 해킹, 방화벽, 개인정보 등의 업무를 지원합니다.\n\n빅데이터 업무에서는 빅데이터, 데이터, 통계, 데이터 분석 등의 업무를 지원합니다.\n\nIT & 빅데이터에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 일반 휴대용 저장매체와 비밀 저장매체 관리요령은 어떻게 되나요?	it_bigdata	\N	2025-09-10 15:06:46.599071	\N
31	\N	text	1	홍보를 선택하셨군요! 홍보 업무에서는 홍보, 홈페이지, 보도, 콘텐츠, 부기 등의 업무를 지원합니다.\n\n홍보에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 미디어 홍보 협업 절차에 대해서 알려주세요.	promotion	\N	2025-09-10 15:06:46.599071	\N
32	\N	text	1	기록물을 선택하셨군요! 기록물 업무에서는 기록물, 보존, 문서관리, 국가기록원, 기록 등의 업무를 지원합니다.\n\n기록물에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 비밀기록물이란 어떠한 기록물을 나타내는 것인가요?	record	\N	2025-09-10 15:06:46.599071	\N
39	37	message	1	{"text": "부기주무관 사용 방법이 궁금해요", "label": "답변보기"}	\N	\N	2025-09-10 15:06:46.602976	\N
40	38	message	1	{"text": "2025년 축제 편성 총괄 담당자는 누구인가요?", "label": "답변보기"}	\N	\N	2025-09-10 15:06:46.602976	\N
35	\N	text	1	부기주무관에 궁금한 자주 묻는 질문을 확인하고, 답변을 확인해 보세요.	\N	\N	2025-09-10 15:06:46.602976	\N
36	\N	button_carousel	2	{"alt_text": "FAQ"}	\N	\N	2025-09-10 15:06:46.602976	\N
37	36	button	1	{"text": "부기주무관 사용 방법이 궁금해요"}	\N	\N	2025-09-10 15:06:46.602976	\N
38	36	button	2	{"text": "2025년 축제 편성 총괄 담당자는 누구인가요?"}	\N	\N	2025-09-10 15:06:46.602976	\N
41	36	text	1	자주 묻는 질문을 수집 중입니다. 	faq	\N	2025-09-19 00:00:00	\N
6	3	uri	2	{"label": "지원 업무 상세 보기", "uri": "https://busanai.busan.go.kr/views/guide"}	\N	\N	2025-09-10 15:06:46.548392	\N
3	2	carousel_column	1	{"image_url": "https://busanai.busan.go.kr/views/assets/images/c1.png", "text": "AI 부기주무관이 지원하는 업무를 확인해보세요."}	\N	\N	2025-09-10 15:06:46.548392	\N
26	\N	text	1	예산회계를 선택하셨군요! 예산회계는 예산회계 및 지원사업 업무를 지원합니다.\n\n예산회계 업무에서는 예산, 회계, 지출, 계약, 부정수급, 재정, 결산, 입찰, 구매, 국비, 시비매칭 등의 업무를 지원합니다.\n\n지원사업 업무에서는 지원사업, 공모사업, 보조사업, 지원금, 공모, 신청, 선정, 지원 등의 업무를 지원합니다.\n\n예산회계에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 회계연도에 속하는 세입세출의 출납에 관한 사무는 언제까지 완료해야하나요?	budget_accounting	\N	2025-09-10 15:06:46.599071	\N
33	\N	text	1	대외협력을 선택하셨군요! 대외협력 업무에서는 민간단체, 공공기관, 부울경, 위원회, 업무협약 등의 업무를 지원합니다.\n\n민간단체 업무에서는 민간단체, 비영리, 보조금 등의 업무를 지원합니다.\n\n공공기관 업무에서는 공공기관, 공기업, 출자, 출연, 지방공기업 업무를 지원합니다.\n\n부울경 업무에서는 부울경, 경남, 울산, 광역, 초광역, 경제동맹, 협력 업무를 지원합니다.\n\n위원회 업무에서는 위원회, 심의회, 협의회 등의 업무를 지원합니다.\n\n업무협약 업무에서는 MOU, 협약, 업무협약 등의 업무를 지원합니다.\n\n대외협력에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 지방출자출연법 시행령 총칙의 내용을 알려주세요.	external_cooper	\N	2025-09-10 15:06:46.599071	\N
34	\N	text	1	안전∙환경을 선택하셨군요! 안전∙환경 업무에서는 환경지키미, 안전지키미 등의 업무를 지원합니다.\n\n환경지키미 업무에서는 환경, 환경민원, 환경부담금, 대기, 수질, 소음, 폐기물, 하천, 하수도등의 업무를 지원합니다.\n\n안전지키미 업무에서는 안전, 재난, 응급, 소방, 방재, 비상, 중대재해, 원자력, 사고, 침수, 싱크홀 등의 업무를 지원합니다.\n\n안전∙환경에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 부산시에서 발생한 빛공해 관련 민원의 추세를 분석해주세요.	safety_environment	\N	2025-09-10 15:06:46.599071	\N
\.


--
-- TOC entry 3476 (class 0 OID 17157)
-- Dependencies: 225
-- Data for Name: TB_STATIC_MESSAGE_FROM_INTENT; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."TB_STATIC_MESSAGE_FROM_INTENT" (id, intent_id, intent_name, message, created_at) FROM stdin;
2	901	구내식당	부산시청 직원식당은 평일 운영되며, 매주 수요일 및 금요일 석식 미운영입니다.\n식사요금은 조식(08:00~09:00) 2,500원, 중식(11:30~13:30) 5,000원, 석식(17:30~18:50) 5,000원 이며,\n주간 메뉴는 아래에서 확인 하실 수 있습니다.\n\nhttp://99.1.1.29/brd/mywork/?brd_menu_div=1&contsType=list&brd_seq=1268#tabGroup=A#contsType=list#contsUrl=#tabIndex=0#isActive=true#page=1#brd_seq=1268#cate_seq=#brd_nm=%EC%A3%BC%EA%B0%84%EC%8B%9D%EB%8B%A8#brd_typ_cd=1#isRead=#\n\n* 위 메뉴는 사정에 따라 변경될 수 있습니다. \n\n* 잔반은 국그릇에 모아서 반납해주시고, 먹을 만큼 음식 담아 주세요! 환경 보호를 위해 잔반 줄이기 캠페인에 적극 참여 부탁드립니다. \n\n* 매일 국의 염도를 측정하여 성인의 건강한 염도 기준을 준수하고 있습니다. \n(국/탕류 0.6~0.7%, 찌개류 0.9~1.0%)\n\n* 부산시청 직원식당은 안전하고 위생적인 식사 제공을 위해 위생점검 및 조리기구 미생물 검사(반기별)를 실시하고 있습니다.	2025-11-25 14:05:34.681212
\.


--
-- TOC entry 3497 (class 0 OID 0)
-- Dependencies: 219
-- Name: TB_CHAT_SESSION_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."TB_CHAT_SESSION_id_seq"', 1, false);


--
-- TOC entry 3498 (class 0 OID 0)
-- Dependencies: 221
-- Name: TB_CHAT_SUMMARY_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."TB_CHAT_SUMMARY_id_seq"', 1, false);


--
-- TOC entry 3499 (class 0 OID 0)
-- Dependencies: 224
-- Name: TB_STATIC_FEEDBACK_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."TB_STATIC_FEEDBACK_id_seq"', 1, false);


--
-- TOC entry 3500 (class 0 OID 0)
-- Dependencies: 226
-- Name: TB_STATIC_MESSAGE_FROM_INTENT_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."TB_STATIC_MESSAGE_FROM_INTENT_id_seq"', 2, true);


--
-- TOC entry 3302 (class 2606 OID 16418)
-- Name: TB_CHAT_HISTORY TB_CHAT_HISTORY_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_CHAT_HISTORY"
    ADD CONSTRAINT "TB_CHAT_HISTORY_pkey" PRIMARY KEY (chat_session_id, chat_number);


--
-- TOC entry 3305 (class 2606 OID 16420)
-- Name: TB_CHAT_SESSION TB_CHAT_SESSION_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_CHAT_SESSION"
    ADD CONSTRAINT "TB_CHAT_SESSION_pkey" PRIMARY KEY (id);


--
-- TOC entry 3308 (class 2606 OID 16422)
-- Name: TB_CHAT_SUMMARY TB_CHAT_SUMMARY_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_CHAT_SUMMARY"
    ADD CONSTRAINT "TB_CHAT_SUMMARY_pkey" PRIMARY KEY (id);


--
-- TOC entry 3310 (class 2606 OID 16424)
-- Name: TB_SETTING TB_SETTING_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_SETTING"
    ADD CONSTRAINT "TB_SETTING_pkey" PRIMARY KEY (key);


--
-- TOC entry 3312 (class 2606 OID 16426)
-- Name: TB_STATIC_FEEDBACK TB_STATIC_FEEDBACK_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_STATIC_FEEDBACK"
    ADD CONSTRAINT "TB_STATIC_FEEDBACK_pkey" PRIMARY KEY (id);


--
-- TOC entry 3317 (class 2606 OID 17165)
-- Name: TB_STATIC_MESSAGE_FROM_INTENT TB_STATIC_MESSAGE_FROM_INTENT_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_STATIC_MESSAGE_FROM_INTENT"
    ADD CONSTRAINT "TB_STATIC_MESSAGE_FROM_INTENT_pkey" PRIMARY KEY (id);


--
-- TOC entry 3306 (class 1259 OID 16429)
-- Name: IDX_CHAT_SUMMARY; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX "IDX_CHAT_SUMMARY" ON public."TB_CHAT_SUMMARY" USING btree (chat_session_id, start_number, end_number);


--
-- TOC entry 3303 (class 1259 OID 16430)
-- Name: IDX_USER_BOT; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX "IDX_USER_BOT" ON public."TB_CHAT_SESSION" USING btree (user_id, bot_id, created_at);


--
-- TOC entry 3313 (class 1259 OID 16431)
-- Name: ix_TB_STATIC_FEEDBACK_from_postback; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_TB_STATIC_FEEDBACK_from_postback" ON public."TB_STATIC_FEEDBACK" USING btree (from_postback);


--
-- TOC entry 3314 (class 1259 OID 16432)
-- Name: ix_TB_STATIC_FEEDBACK_to_postback; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_TB_STATIC_FEEDBACK_to_postback" ON public."TB_STATIC_FEEDBACK" USING btree (to_postback);


--
-- TOC entry 3318 (class 1259 OID 17166)
-- Name: ix_TB_STATIC_MESSAGE_FROM_INTENT_intent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_TB_STATIC_MESSAGE_FROM_INTENT_intent_id" ON public."TB_STATIC_MESSAGE_FROM_INTENT" USING btree (intent_id);


--
-- TOC entry 3319 (class 1259 OID 17167)
-- Name: ix_TB_STATIC_MESSAGE_FROM_INTENT_intent_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_TB_STATIC_MESSAGE_FROM_INTENT_intent_name" ON public."TB_STATIC_MESSAGE_FROM_INTENT" USING btree (intent_name);


--
-- TOC entry 3315 (class 1259 OID 17327)
-- Name: ix_tb_static_feedback_bot_service; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tb_static_feedback_bot_service ON public."TB_STATIC_FEEDBACK" USING btree (bot_service);


--
-- TOC entry 3320 (class 2606 OID 16433)
-- Name: TB_CHAT_HISTORY TB_CHAT_HISTORY_chat_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_CHAT_HISTORY"
    ADD CONSTRAINT "TB_CHAT_HISTORY_chat_session_id_fkey" FOREIGN KEY (chat_session_id) REFERENCES public."TB_CHAT_SESSION"(id);


--
-- TOC entry 3321 (class 2606 OID 16438)
-- Name: TB_CHAT_SUMMARY TB_CHAT_SUMMARY_chat_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_CHAT_SUMMARY"
    ADD CONSTRAINT "TB_CHAT_SUMMARY_chat_session_id_fkey" FOREIGN KEY (chat_session_id) REFERENCES public."TB_CHAT_SESSION"(id);


--
-- TOC entry 3322 (class 2606 OID 16443)
-- Name: TB_STATIC_FEEDBACK TB_STATIC_FEEDBACK_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TB_STATIC_FEEDBACK"
    ADD CONSTRAINT "TB_STATIC_FEEDBACK_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES public."TB_STATIC_FEEDBACK"(id);


--
-- TOC entry 3483 (class 0 OID 0)
-- Dependencies: 217
-- Name: TABLE "TB_CHAT_HISTORY"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."TB_CHAT_HISTORY" TO appuser;


--
-- TOC entry 3484 (class 0 OID 0)
-- Dependencies: 218
-- Name: TABLE "TB_CHAT_SESSION"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."TB_CHAT_SESSION" TO appuser;


--
-- TOC entry 3486 (class 0 OID 0)
-- Dependencies: 219
-- Name: SEQUENCE "TB_CHAT_SESSION_id_seq"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public."TB_CHAT_SESSION_id_seq" TO appuser;


--
-- TOC entry 3487 (class 0 OID 0)
-- Dependencies: 220
-- Name: TABLE "TB_CHAT_SUMMARY"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."TB_CHAT_SUMMARY" TO appuser;


--
-- TOC entry 3489 (class 0 OID 0)
-- Dependencies: 221
-- Name: SEQUENCE "TB_CHAT_SUMMARY_id_seq"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public."TB_CHAT_SUMMARY_id_seq" TO appuser;


--
-- TOC entry 3490 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE "TB_SETTING"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."TB_SETTING" TO appuser;


--
-- TOC entry 3491 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE "TB_STATIC_FEEDBACK"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."TB_STATIC_FEEDBACK" TO appuser;


--
-- TOC entry 3493 (class 0 OID 0)
-- Dependencies: 224
-- Name: SEQUENCE "TB_STATIC_FEEDBACK_id_seq"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public."TB_STATIC_FEEDBACK_id_seq" TO appuser;


--
-- TOC entry 3494 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE "TB_STATIC_MESSAGE_FROM_INTENT"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."TB_STATIC_MESSAGE_FROM_INTENT" TO appuser;


--
-- TOC entry 3496 (class 0 OID 0)
-- Dependencies: 226
-- Name: SEQUENCE "TB_STATIC_MESSAGE_FROM_INTENT_id_seq"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public."TB_STATIC_MESSAGE_FROM_INTENT_id_seq" TO appuser;


-- Completed on 2025-12-03 15:01:55

--
-- PostgreSQL database dump complete
--
