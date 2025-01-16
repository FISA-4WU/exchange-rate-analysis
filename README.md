Check out the live app here: [Exchange Rate Analysis](https://4wmnunivs.streamlit.app/)

[![Watch the video](https://img.youtube.com/vi/영상_ID/0.jpg)](https://youtu.be/AG9lpqZ9aWs)


### 💡 아이디어 배경
해외여행을 준비하는 사람들에게 **환전 시점**은 비용 절감의 중요한 요소입니다. 환율 변동성을 고려하지 않고 환전할 경우, **불필요한 비용**이 발생할 수 있다는 점에서 착안했습니다. 여행 전에 **환전하기 가장 좋은 시점**을 안내하고, 이를 통해 사용자에게 **실질적인 금전적 이득**을 제공하는 서비스를 제공하고자 했습니다.

---

### 🧑‍💻 목적
- 사용자에게 국가와 날짜를 입력받아 최신 환율 정보를 제공하며, 과거 데이터와 예측 모델을 활용해 환율 변동을 분석합니다.
- 예측 결과를 기반으로 사용자가 최적의 환전 시점을 파악할 수 있도록 지원합니다.

---

### 🎯 기대효과
#### **위비트래블 체크카드**
![위비트래블 체크카드](https://d1c5n4ri2guedi.cloudfront.net/card/2700/card_img/34201/2700card.png)
- 환율 예측 및 최적 환전 시점 안내 기능 추가 시,
  - 사용자들에게 **환율 관리의 편의성** 제공으로 **서비스 경쟁력** 강화 가능  
  - 여행 준비 과정에서 환전과 결제까지 **원스톱**으로 해결  
  - 여행객뿐만 아니라 **투자 및 환전 관리에 관심이 있는 고객층**까지 사용자 범위 확대 가능  

---

### ⚙️ 기능
1. 사용자가 설정한 국가의 최근 한 달간 환율 변동성 분석 제공
2. 최근 일주일 동안 주요 국가들의 세계 환율 변동 동향 시각화 및 제공
3. 과거 데이터와 예측 모델을 기반으로 한 환율 추이 예측 및 최적 환전 시점 추천

---

### 📊 사용 데이터
- 한국수출입은행 환율정보 Open API ➡️ [Click!](https://www.koreaexim.go.kr/ir/HPHKIR020M01?apino=2&viewtype=C&searchselect=&searchword=)
- 우리은행 환율정보 Open API ➡️ [Click!](https://spib.wooribank.com/pib/Dream?withyou=CMCOM0186)

---

### 📄 페이지별 설명
#### **[ app.py ]**
- 서비스 소개  
- 메인 페이지

#### **[ crawling.py ]**
- 최근 5년치 우리은행 환율 데이터를 크롤링 및 분석
- Scikit-learn 라이브러리의 RandomForestRegressor를 활용하여 환율 추이를 예측
- 사용자 설정 기간 내 가장 낮은 환율이 예상되는 날짜 5개를 추천

#### **[ map.py ]**
- 최근 7일간 세계 환율 변동 추이 지도
- Plotly의 scatter_geo를 활용하여 세계 환율 변동 시각화
- 환율 변동성을 점의 크기(scatter size)로 반영하여 직관적 데이터 표현

#### **[ exchange_rate.py ]**
- 실시간 환율 정보를 기반으로 환율 계산 제공
- 환율 변동 데이터를 시각화하여 과거 추세를 한눈에 확인 가능
- 환율의 최대값, 최소값, 평균값을 제공하여 데이터의 분포와 특징을 파악

---

### ⚒️ Tools
![Python](https://img.shields.io/badge/python-3776AB.svg?&style=for-the-badge&logo=python&logoColor=white)
![streamlit](https://img.shields.io/badge/streamlit-FF4B4B.svg?&style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikitlearn-F7931E.svg?&style=for-the-badge&logo=scikitlearn&logoColor=white)
![plotly](https://img.shields.io/badge/plotly-3F4F75.svg?&style=for-the-badge&logo=plotly&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458.svg?&style=for-the-badge&logo=pandas&logoColor=white)
![numpy](https://img.shields.io/badge/numpy-013243.svg?&style=for-the-badge&logo=numpy&logoColor=white)
![GitHub](https://img.shields.io/badge/github-181717.svg?&style=for-the-badge&logo=github&logoColor=white)
![notion](https://img.shields.io/badge/notion-000000.svg?&style=for-the-badge&logo=notion&logoColor=white)
![Figma](https://img.shields.io/badge/figma-F24E1E.svg?&style=for-the-badge&logo=figma&logoColor=white)

---

### 🔧 트러블슈팅 회고
#### 1. 성능 관련 문제
- **모델 성능 개선**
  - **Before**: 첫 번째 모델 [MAE: **3.69**, MSE: **22.13**, R²: **0.86**]
  - **After**: 하이퍼파라미터를 최적화한 모델 [MAE: **2.12**, MSE: **10.85**, R²: **0.92**]
  - 결과적으로 예측 정확도 향상 및 오차 감소

- **크롤링 시간 단축**
  - Request 캐싱을 도입하여 응답 시간 개선 진행 중

#### 2. 데이터 분석 과정 문제
- **기간별 환율 조회 API 부재**
  - 환율 데이터를 기간별로 조회할 수 있는 API가 없어 웹 크롤링을 통해 데이터를 수집
  - 크롤링 데이터를 시각화 및 분석에 활용 가능한 형태로 변환

- **특정 데이터 추출 문제**
  - 혼재된 데이터에서 매매기준율만 추출하는 함수 구현

#### 3. 협업 문제
- **Git 충돌 문제**
  - Git Flow를 도입해 브랜치별 작업 분리 및 Pull Request로 코드 리뷰 진행

![git flow](pages/git%20flow.png)
