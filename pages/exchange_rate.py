import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import streamlit as st
from matplotlib import rc
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

API_KEY = st.secrets['API_KEY']
# API_KEY = os.environ.get('API_KEY')

# 한글 폰트 설정
rc('font', family='Arial')  # 윈도우의 맑은 고딕 폰트를 사용
plt.rcParams['axes.unicode_minus'] = False

# 환율 정보를 국가명으로 변환하는 딕셔너리 불러오기
def load_currency_to_country():
    with open("pages/country.json", "r", encoding="utf-8") as file:
        return json.load(file)

currency_to_country = load_currency_to_country()  # 외부 파일에서 불러오기

# API 설정
API_URL = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"

# 함수: 특정 날짜의 환율 데이터 가져오기
def fetch_exchange_rate_data(date):
    params = {
        "authkey": API_KEY,
        "searchdate": date,
        "data": "AP01"  # 환율 정보 코드
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API 호출 실패: 상태 코드 {response.status_code}")
        return None

# 함수: 일주일치 데이터 가져오기 
def fetch_monthly_data():
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime('%Y%m%d') for i in range(3)] # 30일 변환 필수(마지막!!!)  

    all_data = []
    for date in dates:
        daily_data = fetch_exchange_rate_data(date)
        if daily_data:
            for item in daily_data:
                # 통화 코드를 나라 이름으로 변환
                country_name = currency_to_country.get(item["cur_unit"], item["cur_unit"])  # 통화 코드가 없으면 그대로 사용
                all_data.append({
                    "날짜": date,
                    "통화 코드": item["cur_unit"],
                    "나라 이름": country_name,  # 나라 이름 추가
                    "통화명": item["cur_nm"],
                    "매매 기준율 (KRW)": float(item["deal_bas_r"].replace(",", ""))
                })
    return pd.DataFrame(all_data)

def calculate_daily_change_rate(data):
    data = data.sort_values(by="날짜")  # 날짜 기준으로 정렬
    data["전날 환율"] = data["매매 기준율 (KRW)"].shift(1)  # 전날 환율
    data["변동률 (%)"] = ((data["매매 기준율 (KRW)"] - data["전날 환율"]) / data["전날 환율"]) * 100
    return data.dropna()  # 첫 번째 행은 변동률 계산 불가로 제거

# Streamlit UI
st.title("📈 환율 계산기 및 변동성 분석")
st.markdown("수출입은행 API를 사용하여 환율 계산 및 최근 일주일치 환율 변동을 시각화합니다.")

# 환율 계산기
st.subheader("환율 변환기")

# # 사용자 입력
# col1, col2 = st.columns(2)
# with col1:
#     # 나라의 기본값을 "미국"으로 설정
#     selected_country = st.selectbox("나라를 선택하세요:", list(currency_to_country.values()), index=list(currency_to_country.values()).index("미국"))
# with col2:
#     selected_date = st.date_input("날짜를 선택하세요:", value=datetime.now(), min_value=datetime.now() - timedelta(days=30), max_value=datetime.now())

def get_user_input():
    # 사용자 입력
    col1, col2 = st.columns(2)
    
    with col1:
        # 나라의 기본값을 "미국"으로 설정
        selected_country = st.selectbox("나라를 선택하세요:", list(currency_to_country.values()), index=list(currency_to_country.values()).index("미국"))
        
    with col2:
        selected_date = st.date_input("날짜를 선택하세요:", value=datetime.now(), min_value=datetime.now() - timedelta(days=30), max_value=datetime.now())
        
    return selected_country, selected_date


# get_user_input 함수 호출
selected_country, selected_date = get_user_input()

amount = st.number_input("변환할 금액을 입력하세요:", min_value=0.0, value=1.0)

# 데이터 필터링
selected_date_str = selected_date.strftime('%Y%m%d')
data = fetch_exchange_rate_data(selected_date_str)

if data:
    data_df = pd.DataFrame(data)
    data_df["매매 기준율 (KRW)"] = data_df["deal_bas_r"].str.replace(",", "").astype(float)
    data_df["나라 이름"] = data_df["cur_unit"].map(currency_to_country)

    country_data = data_df[data_df["나라 이름"] == selected_country]

    if not country_data.empty:
        exchange_rate = country_data["매매 기준율 (KRW)"].iloc[0]
        currency_code = country_data["cur_unit"].iloc[0]

        # 환율 계산
        converted_amount = amount * exchange_rate

        # 변환 결과 출력
        st.metric(label="변환할 금액", value=f"{amount:.2f} {currency_code}")
        st.metric(label="변환된 금액", value=f"{converted_amount:.2f} KRW")

# 환율 변동성 분석
st.subheader("환율 변동성 분석")
st.markdown("환율 데이터를 사용하여 일별 변동률을 계산하고 상승/하락을 시각화합니다.")

# 데이터 로드
# st.write("환율 데이터를 불러오는 중입니다...")
data = fetch_monthly_data()

if not data.empty:
    plt.style.use('fivethirtyeight')  # 그래프 스타일 변경
    # 선택된 국가 데이터
    selected_data = data[data["나라 이름"] == selected_country]

    if selected_data.empty:
        st.error("분석할 데이터를 찾을 수 없습니다.")
    else:
        # 변동률 계산
        analyzed_data = calculate_daily_change_rate(selected_data)

        # 최댓값, 최솟값, 평균값 계산
        max_value = selected_data["매매 기준율 (KRW)"].max()
        min_value = selected_data["매매 기준율 (KRW)"].min()
        avg_value = selected_data['매매 기준율 (KRW)'].mean()

        # 해당 값에 주석 달기
        max_date = selected_data[selected_data["매매 기준율 (KRW)"] == max_value]["날짜"].iloc[0]
        min_date = selected_data[selected_data["매매 기준율 (KRW)"] == min_value]["날짜"].iloc[0]

        # 그래프 스타일 변경: 어두운 배경
        #plt.style.use('dark_background')

        # Subplot 설정 (행 1, 열 2)
        fig, ax = plt.subplots(1, 2, figsize=(20, 8))

         # 첫 번째 그래프: 환율 변동
        ax[0].plot(
            pd.to_datetime(selected_data["날짜"]),
            selected_data["매매 기준율 (KRW)"],
            label=f'{selected_country} 환율',
            color='orange',
            marker='o', markersize=8  # 마커 크기 조정
        )
        ax[0].set_xlabel('date', fontsize=20)
        ax[0].set_ylabel('the standard rate of trading (KRW)', fontsize=20)
        # ax[0].set_title(f"{selected_country} Exchange rate fluctuations (last 1 month)", fontsize=25, fontweight='bold')
        ax[0].set_title(f"Exchange rate fluctuations (last 1 month)", fontsize=25, fontweight='bold')
        ax[0].legend(fontsize=20)
        ax[0].grid(alpha=0.5, linestyle='--')

        # 최댓값, 최솟값, 평균값 표시
        ax[0].scatter(pd.to_datetime(max_date), max_value, color='red', label=f'Max value: {max_value} (date: {max_date})', zorder=5, s=100)
        ax[0].scatter(pd.to_datetime(min_date), min_value, color='blue', label=f'Min value: {min_value} (date: {min_date})', zorder=5, s=100)
        ax[0].axhline(y=avg_value, color='green', linestyle='--', label=f'Avg value: {avg_value:.2f}')  # 평균값 라인 추가

        # 최댓값, 최솟값을 강조하는 텍스트 추가
        ax[0].annotate(f'{max_value}', 
                       (pd.to_datetime(max_date), max_value),
                       textcoords="offset points", 
                       xytext=(-10,0), 
                       ha='right', fontsize=18, fontweight='bold', color='red')

        ax[0].annotate(f'{min_value}', 
                       (pd.to_datetime(min_date), min_value),
                       textcoords="offset points", 
                       xytext=(15,0), 

                       ha='left', fontsize=18, fontweight='bold', color='blue')
        ax[0].annotate(f'{avg_value:.2f}', 
                       (pd.to_datetime(min_date), avg_value),
                       textcoords="offset points", 
                       xytext=(-10,10), 
                       ha='left', fontsize=18, fontweight='bold', color='green')

        # 두 번째 그래프: 변동률 막대 그래프
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

        colors = ["red" if x > 0 else "blue" for x in analyzed_data["변동률 (%)"]]
        ax[1].bar(pd.to_datetime(analyzed_data["날짜"]), analyzed_data["변동률 (%)"], color=colors, edgecolor="black")
        ax[1].axhline(y=0, color='gray', linestyle='--', linewidth=1)  # 기준선(0%)
        ax[1].set_xlabel("date", fontsize=20)
        ax[1].set_ylabel("rate of change (%)", fontsize=20)
        ax[1].set_title(f"Exchange Rate Change (Up/Down)", fontsize=25, fontweight="bold")
        ax[1].grid(alpha=0.5, linestyle="--")
        ax[1].tick_params(axis="x", rotation=45)

        # Streamlit에 그래프 출력
        st.pyplot(fig)

else:
    st.error("한 달치 데이터를 불러올 수 없습니다.")
