--
-- PostgreSQL database dump
--

-- Dumped from database version 17.6 (Debian 17.6-1.pgdg13+1)
-- Dumped by pg_dump version 17.5

-- Started on 2025-09-10 15:16:00 KST

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

--
-- TOC entry 3440 (class 0 OID 16404)
-- Dependencies: 223
-- Data for Name: TB_STATIC_FEEDBACK; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."TB_STATIC_FEEDBACK" (id, parent_id, message_type, sort_number, content, from_postback, to_postback, created_at) FROM stdin;
1	\N	text	1	안녕하세요. AI맞춤 행정업무를 지원하는 AI 부기주무관 입니다. 업무에 궁금한 점을 바로 질문하시거나 아래에서 해당하는 질문을 클릭해주세요.	start_service	\N	2025-09-10 15:06:46.548392
2	\N	main_carousel	2	{"alt_text": "AI 부기주무관이 지원 업무/자주묻는 질문"}	start_service	\N	2025-09-10 15:06:46.548392
5	3	message	1	{"label": "업무 영역", "text": "AI 부기주무관 지원 업무 영역"}	\N	task_area	2025-09-10 15:06:46.548392
7	4	message	1	{"label": "FAQ", "text": "FAQ"}	\N	faq	2025-09-10 15:06:46.548392
8	4	message	2	{"label": "나의 최근 질문", "text": "나의 최근 질문"}	\N	recent_questions	2025-09-10 15:06:46.548392
9	\N	text	1	업무영역을 선택하셨군요! AI 부기주무관이 지원하는 업무 구분은 아래와 같습니다. 해당하는 업무를 클릭하면 상세한 설명을 보실 수 있습니다.	task_area	\N	2025-09-10 15:06:46.548392
10	\N	button_template	2	{"alt_text": "AI 부기주무관 지원 업무"}	task_area	\N	2025-09-10 15:06:46.548392
11	10	message	1	{"label": "시민서비스", "text": "시민서비스"}	\N	citizen_service	2025-09-10 15:06:46.548392
12	10	message	1	{"label": "예산회계", "text": "예산회계"}	\N	budget_accounting	2025-09-10 15:06:46.548392
13	10	message	1	{"label": "문서봇", "text": "문서봇"}	\N	document_bot	2025-09-10 15:06:46.548392
14	10	message	1	{"label": "법무∙특사경", "text": "법무∙특사경"}	\N	law	2025-09-10 15:06:46.548392
15	10	message	1	{"label": "인사∙복지∙교육", "text": "인사∙복지∙교육"}	\N	employee_welfare	2025-09-10 15:06:46.548392
16	10	message	1	{"label": "IT & 빅데이터", "text": "IT & 빅데이터"}	\N	it_bigdata	2025-09-10 15:06:46.548392
17	10	message	1	{"label": "홍보", "text": "홍보"}	\N	promotion	2025-09-10 15:06:46.548392
18	10	message	1	{"label": "기록물", "text": "기록물"}	\N	record	2025-09-10 15:06:46.548392
19	10	message	1	{"label": "대외협력", "text": "대외협력"}	\N	external_cooper	2025-09-10 15:06:46.548392
20	10	message	1	{"label": "안전∙환경", "text": "안전∙환경"}	\N	safety_environment	2025-09-10 15:06:46.548392
21	\N	text	1	최근 부기주무관에 문의한 질문 내역을 확인할 수 있습니다.	recent_questions	\N	2025-09-10 15:06:46.594016
22	\N	button_carousel	2	{"alt_text": "나의 최근 질문"}	recent_questions	\N	2025-09-10 15:06:46.594016
23	22	button	1	{"text": "나의 최근 질문"}	\N	\N	2025-09-10 15:06:46.594016
24	23	message	1	{"text": "나의 최근 질문", "label": "답변보기"}	\N	\N	2025-09-10 15:06:46.594016
25	\N	text	1	시민서비스를 선택하셨군요! 시민서비스는 부산시정, 당직민원, 청사안내 업무를 지원합니다.\n\n부산시정 업무에서는 시정, 시장, 정책, 시민, 부산, 경영관리계획, 기본계획, 중장기, 업무계획, 의전 등의 업무를 지원합니다.\n\n당직민원 업무에서는 민원, 전화 문의, 질문과 답변 업무를 지원합니다.\n\n청사안내 업무에서는 청사, 층별, 부서안내, 건물, 주차, 방문자, 안내 업무를 지원합니다.\n\n시민서비스에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 부산시의 주요 정책은 무엇인가요?	citizen_service	\N	2025-09-10 15:06:46.599071
26	\N	text	1	예산회계를 선택하셨군요! 예산회계는 예산회계 및 지원사업 업무를 지원합니다.\n\n예산회계 업무에서는 예산, 회계, 지출, 계약, 부정수급, 재정, 결산, 입찰, 구매, 국비, 시비매칭 등의 업무를 지원합니다.\n\n지원사업 업무에서는 지원사업, 공모사업, 보조사업, 지원금, 공모, 신청, 선정, 지원 등의 업무를 지원합니다.\n\n예산회계에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 예산 편성 절차는 어떻게 되나요?	budget_accounting	\N	2025-09-10 15:06:46.599071
27	\N	text	1	문서봇을 선택하셨군요! 문서봇 업무에서는 문서작성 등의 업무를 지원합니다.\n\n문서작성 업무에서는 인사말씀, 보도자료, 계획서, 보고자료등 초안생성 업무를 지원합니다.\n\n문서작성에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 보도자료 작성 방법은 무엇인가요?	document_bot	\N	2025-09-10 15:06:46.599071
28	\N	text	1	법무∙특사경을 선택하셨군요! 법무∙특사경 업무에서는 법령, 사법경찰 등의 업무를 지원합니다.\n\n법령 업무에서는 법령, 법률, 조례, 규칙, 시행령, 시행규칙, 규정, 법무, 입법 등의 업무를 지원합니다.\n\n사법경찰 업무에서는 사법경찰, 특사경, 단속, 수사 등의 업무를 지원합니다.\n\n법무∙특사경에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 법령 개정 절차는 어떻게 되나요?	law	\N	2025-09-10 15:06:46.599071
29	\N	text	1	인사∙복지∙교육을 선택하셨군요! 인사∙복지∙교육 업무에서는 직원복지, 교육 등의 업무를 지원합니다.\n\n직원복지 업무에서는 복지, 연가, 건강검진, 출장비, 식당, 휴가, 인사, 채용 등의 업무를 지원합니다.\n\n교육 업무에서는 교육, 훈련, 연수, 인력개발, 직무교육, 시민교육, 강의, 학습, 역량, 개발원 등의 업무를 지원합니다.\n\n인사∙복지∙교육에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 직원 복지 혜택은 어떤 것이 있나요?	employee_welfare	\N	2025-09-10 15:06:46.599071
30	\N	text	1	IT & 빅데이터를 선택하셨군요! IT & 빅데이터 업무에서는 IT, 정보보안, 빅데이터 등의 업무를 지원합니다.\n\nIT 업무에서는 시스템, DRM, PC, 권한, 장애, 전산, 정보통신, 보안, IP, 행정전화 등의 업무를 지원합니다.\n\n정보보안 업무에서는 보안, 해킹, 방화벽, 개인정보 등의 업무를 지원합니다.\n\n빅데이터 업무에서는 빅데이터, 데이터, 통계, 데이터 분석 등의 업무를 지원합니다.\n\nIT & 빅데이터에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 전산 장애 발생 시 어떻게 하나요?	it_bigdata	\N	2025-09-10 15:06:46.599071
31	\N	text	1	홍보를 선택하셨군요! 홍보 업무에서는 홍보, 홈페이지, 보도, 콘텐츠, 부기 등의 업무를 지원합니다.\n\n홍보에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 홍보 자료는 어떻게 제작하나요?	promotion	\N	2025-09-10 15:06:46.599071
32	\N	text	1	기록물을 선택하셨군요! 기록물 업무에서는 기록물, 보존, 문서관리, 국가기록원, 기록 등의 업무를 지원합니다.\n\n기록물에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 기록물 관리 방침은 어떻게 되나요?	record	\N	2025-09-10 15:06:46.599071
4	2	carousel_column	2	{"image_url": "https://f0eb94ba204f.ngrok-free.app/images/c2.png", "text": "AI 부기주무관에 자주묻는 질문을 확인해보세요."}	\N	\N	2025-09-10 15:06:46.548392
6	3	uri	2	{"label": "지원 업무 상세 보기", "uri": "https://f0eb94ba204f.ngrok-free.app/task_detail.html"}	\N	\N	2025-09-10 15:06:46.548392
33	\N	text	1	대외협력을 선택하셨군요! 대외협력 업무에서는 민간단체, 공공기관, 부울경, 위원회, 업무협약 등의 업무를 지원합니다.\n\n민간단체 업무에서는 민간단체, 비영리, 보조금 등의 업무를 지원합니다.\n\n공공기관 업무에서는 공공기관, 공기업, 출자, 출연, 지방공기업 업무를 지원합니다.\n\n부울경 업무에서는 부울경, 경남, 울산, 광역, 초광역, 경제동맹, 협력 업무를 지원합니다.\n\n위원회 업무에서는 위원회, 심의회, 협의회 등의 업무를 지원합니다.\n\n업무협약 업무에서는 MOU, 협약, 업무협약 등의 업무를 지원합니다.\n\n대외협력에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 민간단체 보조금 신청은 어떻게 해야 하나요?	external_cooper	\N	2025-09-10 15:06:46.599071
34	\N	text	1	안전∙환경을 선택하셨군요! 안전∙환경 업무에서는 환경지키미, 안전지키미 등의 업무를 지원합니다.\n\n환경지키미 업무에서는 환경, 환경민원, 환경부담금, 대기, 수질, 소음, 폐기물, 하천, 하수도등의 업무를 지원합니다.\n\n안전지키미 업무에서는 안전, 재난, 응급, 소방, 방재, 비상, 중대재해, 원자력, 사고, 침수, 싱크홀 등의 업무를 지원합니다.\n\n안전∙환경에 관련하여 궁금하신 점을 메시지창에 입력하여 질문해 주세요.\n\n예시 질문: 폐기물 관리 절차는 어떻게 되나요?	safety_environment	\N	2025-09-10 15:06:46.599071
35	\N	text	1	부기주무관에 궁금한 자주 묻는 질문을 확인하고, 답변을 확인해 보세요.	faq	\N	2025-09-10 15:06:46.602976
36	\N	button_carousel	2	{"alt_text": "FAQ"}	faq	\N	2025-09-10 15:06:46.602976
37	36	button	1	{"text": "부기주무관 사용 방법이 궁금해요"}	\N	\N	2025-09-10 15:06:46.602976
38	36	button	2	{"text": "2025년 축제 편성 총괄 담당자는 누구인가요?"}	\N	\N	2025-09-10 15:06:46.602976
39	37	message	1	{"text": "부기주무관 사용 방법이 궁금해요", "label": "답변보기"}	\N	\N	2025-09-10 15:06:46.602976
40	38	message	1	{"text": "2025년 축제 편성 총괄 담당자는 누구인가요?", "label": "답변보기"}	\N	\N	2025-09-10 15:06:46.602976
3	2	carousel_column	1	{"image_url": "https://f0eb94ba204f.ngrok-free.app/images/c1.png", "text": "AI 부기주무관이 지원하는 업무를 확인해보세요."}	\N	\N	2025-09-10 15:06:46.548392
\.


--
-- TOC entry 3447 (class 0 OID 0)
-- Dependencies: 224
-- Name: TB_STATIC_FEEDBACK_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."TB_STATIC_FEEDBACK_id_seq"', 40, true);


-- Completed on 2025-09-10 15:16:00 KST

--
-- PostgreSQL database dump complete
--

