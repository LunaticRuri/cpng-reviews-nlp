
CPNG Reviews Analysis using NLP
======================
현재 프로젝트가 제출된 proposal과 일부 달라짐! 설명 수정 예정

** 쿠팡 리뷰 데이터 분석 및 리뷰 기반 연관 상품 추천 시스템 구현**

**Team 10**
- 팀원 1: 석누리, 2020118013, 문헌정보학과, nuriyonsei@yonsei.ac.kr, https://github.com/LunaticRuri
- 팀원 2: 허원재, 2020195020, 계량위험관리학과, hushpond@gmail.com

연세대학교 텍스트정보처리론 기말 프로젝트 입니다.

## 1. 서론 Introduction
### 1.1 배경 Background
기업이 신제품을 출시하기 위해서, 혹은 이미 출시되어 있는 자사 상품이 시장에서 어떤 경쟁력을 가지고 있는지 조사하기 위해서 소비자들의 성향과 니즈를 분석하는 것은 필수적이다. 이렇게 소비자들이 원하는 것이 무엇인지 직접 파악하는 방법에는 설문조사, 리뷰 분석 등이 있다. 
한편, 소비자는 상품을 구매함에 있어서 원하는 상품을 구매하기 위해 상당히 많은 시간을 투자하여 정보를 탐색하고 이를 소비자의사결정에 반영한다. 이 과정에서 제품 설명란, 리뷰, 사용설명서, 쇼핑몰이 자체 구축한 상품 비교 서비스 등 소비자가 이용하는 정보원은 상당히 많다. 
소비자는 구매의사를 판단하는 ‘최종 의사결정’ 단계에서 다른 사람들이 소비한 상품에 대해 어떻게 생각했는지 확인하고 추측한 후 최종적인 판단을 내린다. 특히 상품에 대한 객관적인 판단 자료가 충분히 확보되지 않은 경우 소비자는 판단을 위한 정보를 찾게 되는데, 이 과정에서 사람들은 ‘다른 사람들이 그 상품을 어떻게 평가했는지’에 의존한다.
이러한 이론적 배경에 근거하여, 우리 조는 ‘리뷰’라는 정보원을 분석할 필요가 있음을 느꼈다. ‘별점’이라는 수치화된 리뷰와 함께, 상품에 대한 소비자의 주관적인 평가가 반영되어 있는 리뷰 분석을 통해 기업은 소비자의 니즈를 분석할 수 있고, 이를 상품 추천 시스템에 반영한다면 좋은 결과를 얻을 수 있으리라 판단했다.

### 1.2 목적 및 필요성 Purpose
추천 상품 시스템은 이커머스 업체들이 가장 공들이는 부분 중 하나이다.
리뷰는 상품의 특성과 소비자의 요구를 가장 잘 드러내는 데이터임에도 불구하고, 상품 리뷰 자체를 큰 비중으로 추천 시스템에 반영하는 경우는 드물다.
특히, 선행 연구 조사를 통해, 리뷰 데이터를 상품

### 1.3 프로젝트 내용 및 의의 Significance
카테고리 별로 쿠팡에서 많이 판매되고 있는 인기 상품들의 리뷰를 임베딩함으로써 상품의 특성을 담아낸 임베딩을 구성할 수 있고,
본 프로젝트에서는 상품 리뷰 데이터만을 가지고도 충분히 실사용 가능한 연관 상품 추천 시스템을 구현할 수 있다는 것,
나아가 사용자가 직접 원하는 긍정적 특성이 담긴 쿼리 문장을 입력, 제시된 추천 상품들을 필터링하여 상품 검색에 있어 사용자 경험을 향상시킬 수 있음을 보이고자 한다.
이는 가치에 비해 추천 시스템에서 상대적으로 적게 사용되고 있는 리뷰의 유용성을 제고하는 계기가 될 것이다.

## 2. 데이터 Data
### 2.1 데이터 수집 Data collection
쿠팡 메인 페이지에서 접근할 수 있는 주요 17개 카테고리와 그 하위 카테고리마다 존재하는 판매량 상위 200개 상품의 리뷰가 본 프로젝트의 타겟 데이터이다.
### 2.2 데이터 설명 Data description
각 리뷰 한 단위가 곧 샘플 하나가 되고, 변인은 상품 종류, 상품명(또는 코드), 별점, 리뷰 raw text 정도가 될 것이다. 수집한 데이터를 어떤 형식으로 저장할 것인지 문제 되는데, 계획 단계에서는 일단 상품 분류별로 JSON 파일을 만들어 이를 처리하는 형태를 상정하였다.

## 3. 방법 Methods
### 3.1 주제 유형 Type of the analysis
프로젝트가 다루고자 하는 주요 분석 유형은 Document Embedding과 Sentimental Analysis이다.

### 3.2 예상되는 난제 Challenges
본 프로젝트에서 가장 중요한 문제는 팀원 모두가 해당 필드 프로그래밍에 익숙하지 않은 상태이기에, 구현 그 자체에서 어려움을 겪을 가능성이 매우 높다. 나아가 실제 프로젝트 개발이 어느 정도 선에서 이루어지는지 파악되지 않으면, 설계 단계에서도 비현실적인 목표 설정과 같은 문제가 생길 우려가 있다.
데이터의 수집 과정에서 쿠팡 상품 페이지가 그렇게 규칙적이지 않기 때문에 상당한 어려움이 있을 것으로 예상된다. 리뷰 데이터는 대체로 정형화되어 있지 않기 때문에, 여기서 원하는 정보를 추출하는 작업은 간단하지 않다. 또한 학습 과정에서 부족한 연산 리소스 문제도 예상할 수 있다... 

## 4. 읽고 참고한 자료 References
- 김영신, 강이주, 이희숙, 정순희, & 허경옥. (2009). 새로 쓰는 소비자의사결정. 주) 교문사, 90-92.
- 이다희, 이원민 & 온병원. (2022). 감성 정보를 반영한 워드 임베딩을 위한 학습 데이터 자동 생성 방안.
- 정세준. (2020). 기계학습을 이용한 Aspect-Based Sentiment Analysis 기반 전기차 요소별 사용자 감성 분석 및 예측 모델링.
- 박호연 & 김경재. (2021). BERT 기반 감성분석을 이용한 추천시스템
- 안은미. (2013). 소비자 심리학. 서울: 박학사. 90. 
- Do, H. H., Prasad, P. W. C., Maag, A., & Alsadoon, A. (2019). Deep learning for aspect-based sentiment analysis: a comparative review. Expert systems with applications, 118, 272-299.
- Ray, B., Garain, A., & Sarkar, R. (2021). An ensemble-based hotel recommender system using sentiment analysis and aspect categorization of hotel reviews. Applied Soft Computing, 98, 106935.
- Arora, S., Liang, Y., & Ma, T. (2017). A simple but tough-to-beat baseline for sentence embeddings. In International conference on learning representations.
- Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2018). Bert: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint arXiv:1810.04805.
- Le, Q., & Mikolov, T. (2014, June). Distributed representations of sentences and documents. In International conference on machine learning (pp. 1188-1196). PMLR.
- Reimers, N., & Gurevych, I. (2019). Sentence-bert: Sentence embeddings using siamese bert-networks. arXiv preprint arXiv:1908.10084.
- Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... & Polosukhin, I. (2017). Attention is all you need. Advances in neural information processing systems, 30.
- [E-commerce] 아마존, 네이버, 쿠팡, 11번가는 리뷰를 어떻게 이해하고 보여줄까? (Aspect-based), 2022년 4월 30일 검색, https://velog.io/@jonas-jun/ABSA사례
