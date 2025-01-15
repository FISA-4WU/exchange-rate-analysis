from st_pages import Page, Section, show_pages, add_page_title, hide_pages
import streamlit as st


add_page_title()

show_pages(
    [   
        Page("app.py", "환율 분석 및 예측", "✈️"),

        #Section("section", "🧙‍♂️"),
        Page("pages/map.py", "세계 환율 변동", "🌏", in_section=True),
        Page("pages/crawling.py", "환율 추이 예측", "🤖", in_section=True),
        Page("pages/exchange_rate.py", "환율 계산 및 시각화", "📈", in_section=True),
    ]
)

hide_pages(["Thank you"])

st.markdown(""" 
            
### 🧑‍💻 목적
* 사용자에게 국가와 날짜를 입력받아 환율 정보를 제공하고, 향후 환율 변동을 예측합니다.
* 예측 결과를 바탕으로 최적 환전 시점을 추천합니다.
           

--- 
            
### ⚙️ 기능
    1️⃣ 원하는 국가 및 기간을 입력받아
    2️⃣ 
            
---

### 📊 사용 데이터 """)
            
st.info("한국수출입은행 환율정보 Open API ➡️ [Click!](https://www.koreaexim.go.kr/ir/HPHKIR020M01?apino=2&viewtype=C&searchselect=&searchword=)")
            

st.markdown("""

---
            
### 📄 페이지별 간단 설명?
* **app.py** : 메인 페이지
* **map.py** : 최근 7일간 세계 환율 변동 추이를 지도 위에 표시. Plotly의 scatter_geo를 사용
* **crawling.py** : 챗지피티 예측 결과 ,, 어쩌고
* **exchange_rate.py** : 환율 계산 및 한달치 환율 변동 시각화

---
            
### ⚒️ Tools
* Python 3
* 시각화나 데이터 분석에 사용한 툴 등

            

""")