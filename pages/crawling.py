
import json
import requests
import pandas as pd
import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import streamlit as st
from bs4 import BeautifulSoup
import time

# country.json 파일 읽기
with open('country.json', 'r', encoding='utf-8') as f:
    country_dict = json.load(f)

# 모든 통화 코드 리스트
currencies = list(country_dict.keys())

# 사용자 입력 받기 (통화 코드와 날짜)
def get_user_input():
    selected_country = st.selectbox("나라를 선택하세요:", list(country_dict.values()))
    selected_date = st.date_input("여행 날짜를 선택하세요:", datetime.date.today() + datetime.timedelta(days=10))  # 기본 10일 후
    selected_country_code = [key for key, value in country_dict.items() if value == selected_country][0]
    return selected_country_code, selected_date

# WooriBank API로 환율 데이터 크롤링 (최적화)
def crawl_exchange_rate_data(start_date, end_date, currency_code):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }

    # 날짜 범위에 맞게 API 요청하기
    body = {
        'BAS_SDT': start_date.strftime('%Y%m%d'),
        'BAS_EDT': end_date.strftime('%Y%m%d'),
        'INQ_DIS': currency_code,
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
    
    # 중복된 날짜 제거 (시간 절약)
    df = pd.DataFrame(exchange_rate_by_date)
    df = df.drop_duplicates(subset=['date'], keep='last')
    return df

# 모델 학습 함수 (최적화)
def train_model(df):
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_year'] = df['date'].dt.dayofyear
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['weekday'] = df['date'].dt.weekday  # 요일 추가
    df['is_weekend'] = (df['weekday'] >= 5).astype(int)  # 주말 여부 추가

    # 'exchange_rate' 컬럼에서 쉼표를 제거하고 float로 변환
    df['exchange_rate'] = df['exchange_rate'].astype(float)

    features = ['day_of_year', 'year', 'month', 'weekday', 'is_weekend']
    target = 'exchange_rate'

    X = df[features]
    y = df[target]

    # RandomForest 모델에서 파라미터 최적화
    model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42, n_jobs=-1, bootstrap=True,
                                  min_samples_leaf=1, min_samples_split=2)
    model.fit(X, y)
    return model

# 예측 함수 (최적화)
def predict_exchange_rate(model, start_date, end_date):
    forecast_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    forecast_data = pd.DataFrame({
        'day_of_year': forecast_dates.dayofyear,
        'year': forecast_dates.year,
        'month': forecast_dates.month,
        'weekday': forecast_dates.weekday,
        'is_weekend': (forecast_dates.weekday >= 5).astype(int)
    })

    # 예측 (벡터화로 처리)
    predicted_values = model.predict(forecast_data)

    forecast_df = pd.DataFrame({
        '날짜': forecast_dates,
        '예측 환율': predicted_values
    })

    return forecast_df

# 성능 평가 함수
def evaluate_model(model, df):
    X = df[['day_of_year', 'year', 'month', 'weekday', 'is_weekend']]
    y_true = df['exchange_rate']

    # 예측
    y_pred = model.predict(X)

    # 성능 평가
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    return mae, mse, r2

# 메인 함수
def main():
    # 시간 측정 시작
    start_time = time.time()
    # 사용자 입력 받기
    selected_country_code, selected_date = get_user_input()

    # 크롤링 시작 날짜와 끝 날짜 설정
    today_date = datetime.date.today()
    search_finish_date = selected_date
    search_start_date = today_date - datetime.timedelta(days=365 * 10)  # 5년치 데이터

    # 전체 데이터 크롤링
    df = crawl_exchange_rate_data(search_start_date, search_finish_date, selected_country_code)

    if df.empty:
        st.write("해당 기간의 환율 데이터가 없습니다.")
        return

    # 모델 학습
    model = train_model(df)

    # 예측된 환율 추출
    forecast_df = predict_exchange_rate(model, today_date, selected_date)

    # 예측된 환율 중에서 최저 2개를 오름차순으로 선택
    lowest_2 = forecast_df.nsmallest(5, '예측 환율')  # 오름차순으로 선택

    # 예측 결과 표시
    st.write(f"{country_dict[selected_country_code]} ({selected_country_code})의 환율 예측:")
    st.write(lowest_2[['날짜', '예측 환율']])

    # 성능 평가
    mae, mse, r2 = evaluate_model(model, df)

    # 실행 시간 계산
    # 시간 측정 종료
    end_time = time.time()
    execution_time = end_time - start_time
    # st.write(f"전체 실행 시간: {execution_time:.2f}초")

    # st.write(f"모델 성능 평가:")
    # st.write(f"MAE (평균 절대 오차): {mae:.2f}")
    # st.write(f"MSE (평균 제곱 오차): {mse:.2f}")
    # st.write(f"R2 (결정 계수): {r2:.2f}")


if __name__ == "__main__":
    main()
