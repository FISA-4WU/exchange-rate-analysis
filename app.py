from st_pages import Page, Section, show_pages, add_page_title, hide_pages
import streamlit as st

add_page_title()

show_pages(
    [   
        #Section("Menu"),
        Page("app.py", "환율 분석 및 예측 서비스", "✈️"),
        Page("pages/recommend.py", "환전 날짜 추천", "🤖", in_section=True),
        Page("pages/map.py", "세계 환율 변동", "🌏", in_section=True),
        Page("pages/exchange_rate.py", "환율 계산 및 시각화", "📈", in_section=True),
    ]
)

hide_pages(["Thank you"])

st.balloons()

st.markdown(""" 
            
### 🧑‍💻 목적
* 사용자에게 국가와 날짜를 입력받아 환율 정보를 제공하고, 향후 환율 변동을 예측합니다.
* 예측 결과를 바탕으로 최적 환전 시점을 추천합니다.
           

--- 
            
### ⚙️ 기능
    1️⃣ 사용자가 설정한 국가의 한달 간 환율 변동성 분석
    2️⃣ 최근 일주일 간 세계 환율 변동 확인
    3️⃣ 환율 추이 예측을 통한 환전 일자 추천
            
---

### 📊 사용 데이터 """)
            
st.info("한국수출입은행 환율정보 Open API ➡️ [Click!](https://www.koreaexim.go.kr/ir/HPHKIR020M01?apino=2&viewtype=C&searchselect=&searchword=)")
            

st.markdown("""

---
            
### 📄 페이지별 설명
##### **[ app.py ]**
    • 메인 페이지   
            
##### **[ crawling.py ]**
    • 환율 추이 예측 페이지        
    • 최근 5년치 우리은행 환율 데이터 -> Scikit-learn
    • 사용자 설정 기간 중 환율이 가장 낮을 것으로 예측되는 날 추천
                
##### **[ map.py ]**
    • 최근 7일간 세계 환율 변동 추이 지도
    • Plotly의 scatter_geo 사용
    • 변동성을 scatter의 size에 반영
            
##### **[ exchange_rate.py ]**
    • 환율 계산기
    • 환율 변동 시각화

---
            
### ⚒️ Tools
* Python 3
* Streamlit
* 시각화나 데이터 분석에 사용한 툴 등

---

### 🤯 회고

""")