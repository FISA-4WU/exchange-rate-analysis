import json
import requests
import pandas as pd
import datetime
from sklearn.ensemble import RandomForestRegressor
import streamlit as st
from bs4 import BeautifulSoup
import plotly.graph_objects as go


st.title("🤖 환전 날짜 추천")
st.markdown('\n\n')

# contry.json 파일 읽기
with open('pages/contry.json', 'r', encoding='utf-8') as f:
    contry_dict = json.load(f)

# 모든 통화 코드 리스트
currencies = list(contry_dict.keys())

# 사용자 입력 받기 (통화 코드와 날짜)
def get_user_input():
    selected_contry = st.selectbox("어디로 여행 가시나요?", list(contry_dict.values()))
    selected_date = st.date_input("언제 출발하시나요?", datetime.date.today() + datetime.timedelta(days=10))  # 기본 10일 후
    selected_contry_code = [key for key, value in contry_dict.items() if value == selected_contry][0]
    return selected_contry_code, selected_date

# WooriBank API로 환율 데이터 크롤링
def crawl_exchange_rate_data(start_date, end_date, currency_code):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }

    # 날짜 범위에 맞게 API 요청하기
    body = {
        'BAS_SDT': start_date.strftime('%Y%m%d'),
        'BAS_EDT': end_date.strftime('%Y%m%d'),
        'BAS_DT': '',
        'CUR_Y': '',
        'CUR_M': '',
        'START_DATE_PRINT': '',
        'END_DATE_PRINT': '',
        'INQ_DIS_K': '',
        'INQ_DIS': currency_code,
        'START_DATE_601_02': start_date.strftime('%Y.%m.%d'),
        'END_DATE_601_02': end_date.strftime('%Y.%m.%d'),
        'mm': '01',
    }

    url = 'https://spib.wooribank.com/pib/jcc?withyou=CMCOM0185&__ID=c012349'
    response = requests.post(url, headers=headers, data=body)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 환율 데이터를 테이블에서 추출
    trs = soup.select('#resultArea_601_02_01 > table > tbody > tr')
    
    exchange_rate_by_date = []
    for tr in trs:
        tds = tr.find_all('td')
        date = datetime.datetime.strptime(tds[0].get_text(), '%Y.%m.%d')  # 첫 번째 <td>에서 날짜 추출
        trading_base_rate = tds[5].get_text(strip=True).replace(',', '')  # 여섯 번째 <td>에서 환율 추출, 쉼표 제거
        try:
            exchange_rate_by_date.append({
                'date': date,
                'currency': currency_code,
                'exchange_rate': float(trading_base_rate)
            })
        except ValueError:
            continue  # 환율이 숫자가 아닌 경우 예외 처리
    
    return exchange_rate_by_date

# 모델 학습 함수
def train_model(df):
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_year'] = df['date'].dt.dayofyear
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.weekday  # 요일 추가
    df['is_weekend'] = (df['weekday'] >= 5).astype(int)  # 주말 여부 추가

    # 'exchange_rate' 컬럼에서 쉼표를 제거하고 float로 변환
    df['exchange_rate'] = df['exchange_rate'].astype(float)

    features = ['day_of_year', 'year', 'month', 'day', 'weekday', 'is_weekend']
    target = 'exchange_rate'

    X = df[features]
    y = df[target]

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    return model

# 예측 함수 (여러 날짜에 대해 예측)
def predict_exchange_rate(model, start_date, end_date, selected_contry_code):
    # 예측할 날짜 범위 생성
    forecast_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    forecast_data = pd.DataFrame({
        'day_of_year': forecast_dates.dayofyear,
        'year': forecast_dates.year,
        'month': forecast_dates.month,
        'day': forecast_dates.day,
        'weekday': forecast_dates.weekday,
        'is_weekend': (forecast_dates.weekday >= 5).astype(int)
    })

    # 예측
    predicted_values = model.predict(forecast_data)

    # 예측 결과를 DataFrame으로 반환
    forecast_df = pd.DataFrame({
        '날짜': forecast_dates,
        '예측 환율': predicted_values
    })

    # 선택된 나라에 대한 예측 결과 반환
    forecast_df['currency'] = selected_contry_code

    # 인덱스 리셋
    forecast_df.reset_index(drop=True, inplace=True)

    return forecast_df

# 메인 함수
def main():
    # 사용자 입력 받기
    selected_contry_code, selected_date = get_user_input()

    # 크롤링 시작 날짜와 끝 날짜 설정
    today_date = datetime.date.today()
    search_finish_date = selected_date
    search_start_date = today_date - datetime.timedelta(days=365 * 5)  # 5년치 데이터

    # 전체 데이터 크롤링
    df = pd.DataFrame(crawl_exchange_rate_data(search_start_date, search_finish_date, selected_contry_code))

    if df.empty:
        st.write("해당 기간의 환율 데이터가 없습니다.")
        return

    # 모델 학습
    model = train_model(df)

    # 예측된 환율 추출
    forecast_df = predict_exchange_rate(model, today_date, selected_date, selected_contry_code)

    # 예측된 환율 중에서 최저 2개를 오름차순으로 선택
    lowest_2 = forecast_df.nsmallest(5, '예측 환율')  # 오름차순으로 선택

    st.markdown("\n\n\n\n\n\n\n\n\n\n")
    # 예측 결과 표시
    st.write(f"{contry_dict[selected_contry_code]} ({selected_contry_code})의 환율이 낮을 것 같은 날을 선정해봤어요  '_'\n 오류가 생기면 깃허브로 연락주세요. 빠른 시일 내에 고치겠습니다.")
    #st.write(lowest_2[['날짜', '예측 환율']])

    # Plotly로 표 생성
    fig = go.Figure(data=[go.Table(
        header=dict(values=['날짜', '예측 환율'], font=dict(size=18, weight='bold'), height=35, align='center'),
        cells=dict(values=[lowest_2['날짜'].astype(str).str[:10], lowest_2['예측 환율'].round(2)],font_size=17,height=30),
    )])

    fig.update_layout(
    height=2000
    )

    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
