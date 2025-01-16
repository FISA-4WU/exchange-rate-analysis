# import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# from datetime import datetime, timedelta
# import requests
# import json

# def get_exchange_rates(search_date, api_key):
#     base_url = 'https://spib.wooribank.com/pib/jcc?withyou=CMCOM0185&__ID=c012349'
#     params = {
#         'authkey': api_key,
#         'searchdate': search_date.strftime('%Y%m%d'),
#         'data': 'AP01'
#     }
    
#     try:
#         response = requests.get(base_url, params=params, verify=False)
#         print("Response status:", response.status_code)  # 응답 상태 코드 출력
#         print("Response data:", response.text)  # 응답 데이터 출력
        
#         if response.status_code != 200:
#             print(f"API 호출 실패. 상태 코드: {response.status_code}")
#             return None
#         data = response.json()
#         if not data:
#             return None
#         return data
#     except requests.exceptions.RequestException as e:
#         print(f"API 요청 오류: {str(e)}")
#         return None

# # 최근 5년간의 환율 데이터를 수집하고 처리하는 함수
# def process_exchange_data(api_key, days=365*5):
#     all_data = []
#     end_date = datetime.now()
#     start_date = end_date - timedelta(days=days)
    
#     current_date = start_date
#     while current_date <= end_date:
#         data = get_exchange_rates(current_date, api_key)
#         if data:
#             for item in data:
#                 item['date'] = current_date.strftime('%Y-%m-%d')
#                 all_data.append(item)
#         current_date += timedelta(days=1)
    
#     if not all_data:
#         print("수집된 데이터가 없습니다.")
#         return pd.DataFrame()
    
#     return pd.DataFrame(all_data)

# # 환율 데이터에서 특성(feature) 엔지니어링을 위한 함수
# def feature_engineering(df):
#     if df.empty:
#         return df
    
#     # 날짜를 기반으로 새로운 피처 생성
#     df['date'] = pd.to_datetime(df['date'])
#     df['day_of_year'] = df['date'].dt.dayofyear
#     df['year'] = df['date'].dt.year
#     df['month'] = df['date'].dt.month
#     df['day'] = df['date'].dt.day
    
#     # deal_bas_r를 숫자로 변환 (문자열에서 숫자형 데이터로 변환)
#     df['deal_bas_r'] = df['deal_bas_r'].str.replace(',', '').astype(float)
    
#     # 결측값 처리: 타겟 변수와 관련된 열에서 결측값을 제거하거나 채움
#     df = df.dropna(subset=['deal_bas_r'])  # deal_bas_r 열에 결측값이 있으면 해당 행을 제거

#     return df

# # RandomForest 모델 학습 함수
# def train_model(df):
#     df_clean = feature_engineering(df)
    
#     if df_clean.empty:
#         print("유효한 데이터가 없습니다.")
#         return None
    
#     X = df_clean[['day_of_year', 'year', 'month', 'day']]  # 예측에 사용할 피처
#     y = df_clean['deal_bas_r']  # 예측할 환율 타겟 변수

#     # 결측값 처리: y에 NaN 값이 있을 경우 이를 처리 (여기서는 제거)
#     y = y.dropna()

#     # y에 NaN 값이 있으면 학습할 수 없으므로, X와 y의 길이가 맞는지 확인
#     if len(X) != len(y):
#         print("X와 y의 길이가 맞지 않습니다. NaN을 처리한 후 다시 시도해 주세요.")
#         return None

#     model = RandomForestRegressor(n_estimators=100)
#     model.fit(X, y)
    
#     return model

# # 예측 결과를 상위 5개 날짜로 반환하는 함수
# def get_top_5_dates(model, df):
#     df_clean = feature_engineering(df)
    
#     if df_clean.empty:
#         print("유효한 데이터가 없습니다.")
#         return None
    
#     X = df_clean[['day_of_year', 'year', 'month', 'day']]
#     df_clean['predicted_rate'] = model.predict(X)
    
#     # 예측된 환율을 기준으로 상위 5개 날짜 선택
#     top_5_dates = df_clean.sort_values(by='predicted_rate', ascending=True).head(5)
    
#     return top_5_dates[['date', 'predicted_rate']]

# # 메인 함수
# def main():
#     api_key = 'RMttRjjtKPYayYWYwHdxVps5r8OSy8Ws'  # 실제 API 키를 입력하세요.
    
#     df = process_exchange_data(api_key)  # 환율 데이터 처리
    
#     if df.empty:
#         print("환율 데이터를 처리할 수 없습니다.")
#         return
    
#     model = train_model(df)  # 모델 학습
    
#     if model:
#         top_5_dates = get_top_5_dates(model, df)
#         if top_5_dates is not None:
#             print("상위 5개의 최저 환율 날짜:")
#             print(top_5_dates)
#         else:
#             print("최저 환율 날짜를 예측할 수 없습니다.")
#     else:
#         print("모델 학습에 실패했습니다.")

# if __name__ == '__main__':
#     main()


# import json
# import requests
# import pandas as pd
# import datetime
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# import streamlit as st
# from bs4 import BeautifulSoup

# # country.json 파일 읽기
# with open('C:/ITStudy/4WU/exchange-rate-analysis/pages/country.json', 'r', encoding='utf-8') as f:
#     country_dict = json.load(f)

# # 모든 통화 코드 리스트
# currencies = list(country_dict.keys())

# # 사용자 입력 받기 (통화 코드와 날짜)
# def get_user_input():
#     selected_country = st.selectbox("나라를 선택하세요:", list(country_dict.values()))
#     selected_date = st.date_input("여행 날짜를 선택하세요:", datetime.date.today() + datetime.timedelta(days=10))  # 기본 10일 후
#     selected_country_code = [key for key, value in country_dict.items() if value == selected_country][0]
#     return selected_country_code, selected_date

# # WooriBank API로 환율 데이터 크롤링
# def crawl_exchange_rate_data(start_date, end_date, currency_code):
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
#     }

#     # 날짜 범위에 맞게 API 요청하기
#     body = {
#         'BAS_SDT': start_date.strftime('%Y%m%d'),
#         'BAS_EDT': end_date.strftime('%Y%m%d'),
#         'BAS_DT': '',
#         'CUR_Y': '',
#         'CUR_M': '',
#         'START_DATE_PRINT': '',
#         'END_DATE_PRINT': '',
#         'INQ_DIS_K': '',
#         'INQ_DIS': currency_code,
#         'START_DATE_601_02': start_date.strftime('%Y.%m.%d'),
#         'END_DATE_601_02': end_date.strftime('%Y.%m.%d'),
#         'mm': '01',
#     }

#     url = 'https://spib.wooribank.com/pib/jcc?withyou=CMCOM0185&__ID=c012349'
#     response = requests.post(url, headers=headers, data=body)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # 환율 데이터를 테이블에서 추출
#     trs = soup.select('#resultArea_601_02_01 > table > tbody > tr')
    
#     exchange_rate_by_date = []
#     for tr in trs:
#         tds = tr.find_all('td')
#         date = datetime.datetime.strptime(tds[0].get_text(), '%Y.%m.%d')  # 첫 번째 <td>에서 날짜 추출
#         trading_base_rate = tds[5].get_text(strip=True).replace(',', '')  # 여섯 번째 <td>에서 환율 추출, 쉼표 제거
#         try:
#             exchange_rate_by_date.append({
#                 'date': date,
#                 'currency': currency_code,
#                 'exchange_rate': float(trading_base_rate)
#             })
#         except ValueError:
#             continue  # 환율이 숫자가 아닌 경우 예외 처리
    
#     return exchange_rate_by_date

# # 모델 학습 함수
# def train_model(df):
#     df['date'] = pd.to_datetime(df['date'])
#     df['day_of_year'] = df['date'].dt.dayofyear
#     df['year'] = df['date'].dt.year
#     df['month'] = df['date'].dt.month
#     df['day'] = df['date'].dt.day
#     df['weekday'] = df['date'].dt.weekday  # 요일 추가
#     df['is_weekend'] = (df['weekday'] >= 5).astype(int)  # 주말 여부 추가

#     # 'exchange_rate' 컬럼에서 쉼표를 제거하고 float로 변환
#     df['exchange_rate'] = df['exchange_rate'].astype(float)

#     features = ['day_of_year', 'year', 'month', 'day', 'weekday', 'is_weekend']
#     target = 'exchange_rate'

#     X = df[features]
#     y = df[target]

#     model = RandomForestRegressor(n_estimators=100)
#     model.fit(X, y)
#     return model


# # 예측 함수 (여러 날짜에 대해 예측)
# def predict_exchange_rate(model, start_date, end_date, selected_country_code):
#     # 예측할 날짜 범위 생성
#     forecast_dates = pd.date_range(start=start_date, end=end_date, freq='D')
#     forecast_data = pd.DataFrame({
#         'day_of_year': forecast_dates.dayofyear,
#         'year': forecast_dates.year,
#         'month': forecast_dates.month,
#         'day': forecast_dates.day,
#         'weekday': forecast_dates.weekday,
#         'is_weekend': (forecast_dates.weekday >= 5).astype(int)
#     })

#     # 예측
#     predicted_values = model.predict(forecast_data)

#     # 예측 결과를 DataFrame으로 반환
#     forecast_df = pd.DataFrame({
#         '날짜': forecast_dates,
#         '예측 환율': predicted_values
#     })

#     # 선택된 나라에 대한 예측 결과 반환
#     forecast_df['currency'] = selected_country_code

#     # 인덱스 리셋
#     forecast_df.reset_index(drop=True, inplace=True)

#     return forecast_df

# # 메인 함수
# def main():
#     # 사용자 입력 받기
#     selected_country_code, selected_date = get_user_input()

#     # 크롤링 시작 날짜와 끝 날짜 설정
#     today_date = datetime.date.today()
#     search_finish_date = selected_date
#     search_start_date = today_date - datetime.timedelta(days=365 * 5)  # 5년치 데이터

#     # 전체 데이터 크롤링
#     df = pd.DataFrame(crawl_exchange_rate_data(search_start_date, search_finish_date, selected_country_code))

#     if df.empty:
#         st.write("해당 기간의 환율 데이터가 없습니다.")
#         return

#     # 모델 학습
#     model = train_model(df)

#     # 예측된 환율 추출
#     forecast_df = predict_exchange_rate(model, today_date, selected_date, selected_country_code)

#     # 예측된 환율 중에서 최저 2개를 오름차순으로 선택
#     lowest_2 = forecast_df.nsmallest(5, '예측 환율')  # 오름차순으로 선택

#     # 예측 결과 표시
#     st.write(f"{country_dict[selected_country_code]} ({selected_country_code})의 환율 예측:")
#     st.write(lowest_2[['날짜', '예측 환율']])


# if __name__ == "__main__":
#     main()


# import json
# import requests
# import pandas as pd
# import datetime
# from sklearn.ensemble import RandomForestRegressor
# import streamlit as st
# from bs4 import BeautifulSoup

# # country.json 파일 읽기
# with open('C:/ITStudy/4WU/exchange-rate-analysis/pages/country.json', 'r', encoding='utf-8') as f:
#     country_dict = json.load(f)

# # 모든 통화 코드 리스트
# currencies = list(country_dict.keys())

# # 사용자 입력 받기 (통화 코드와 날짜)
# def get_user_input():
#     selected_country = st.selectbox("나라를 선택하세요:", list(country_dict.values()))
#     selected_date = st.date_input("여행 날짜를 선택하세요:", datetime.date.today() + datetime.timedelta(days=10))  # 기본 10일 후
#     selected_country_code = [key for key, value in country_dict.items() if value == selected_country][0]
#     return selected_country_code, selected_date

# # WooriBank API로 환율 데이터 크롤링
# def crawl_exchange_rate_data(start_date, end_date, currency_code):
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
#     }

#     # 날짜 범위에 맞게 API 요청하기
#     body = {
#         'BAS_SDT': start_date.strftime('%Y%m%d'),
#         'BAS_EDT': end_date.strftime('%Y%m%d'),
#         'BAS_DT': '',
#         'CUR_Y': '',
#         'CUR_M': '',
#         'START_DATE_PRINT': '',
#         'END_DATE_PRINT': '',
#         'INQ_DIS_K': '',
#         'INQ_DIS': currency_code,
#         'START_DATE_601_02': start_date.strftime('%Y.%m.%d'),
#         'END_DATE_601_02': end_date.strftime('%Y.%m.%d'),
#         'mm': '01',
#     }

#     url = 'https://spib.wooribank.com/pib/jcc?withyou=CMCOM0185&__ID=c012349'
#     response = requests.post(url, headers=headers, data=body)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # 환율 데이터를 테이블에서 추출
#     trs = soup.select('#resultArea_601_02_01 > table > tbody > tr')
    
#     exchange_rate_by_date = []
#     for tr in trs:
#         tds = tr.find_all('td')
#         date = datetime.datetime.strptime(tds[0].get_text(), '%Y.%m.%d')  # 첫 번째 <td>에서 날짜 추출
#         trading_base_rate = tds[5].get_text(strip=True).replace(',', '')  # 여섯 번째 <td>에서 환율 추출, 쉼표 제거
#         try:
#             exchange_rate_by_date.append({
#                 'date': date,
#                 'currency': currency_code,
#                 'exchange_rate': float(trading_base_rate)
#             })
#         except ValueError:
#             continue  # 환율이 숫자가 아닌 경우 예외 처리
    
#     return exchange_rate_by_date

# # 모델 학습 함수
# def train_model(df):
#     df['date'] = pd.to_datetime(df['date'])
#     df['day_of_year'] = df['date'].dt.dayofyear
#     df['year'] = df['date'].dt.year
#     df['month'] = df['date'].dt.month
#     df['day'] = df['date'].dt.day

#     # 'exchange_rate' 컬럼에서 쉼표를 제거하고 float로 변환
#     df['exchange_rate'] = df['exchange_rate'].astype(float)

#     features = ['day_of_year', 'year', 'month', 'day']
#     target = 'exchange_rate'

#     X = df[features]
#     y = df[target]

#     model = RandomForestRegressor(n_estimators=100)
#     model.fit(X, y)
#     return model

# # 예측 함수 (여러 날짜에 대해 예측)
# def predict_exchange_rate(model, start_date, end_date, selected_country_code):
#     # 예측할 날짜 범위 생성
#     forecast_dates = pd.date_range(start=start_date, end=end_date, freq='D')
#     forecast_data = pd.DataFrame({
#         'day_of_year': forecast_dates.dayofyear,
#         'year': forecast_dates.year,
#         'month': forecast_dates.month,
#         'day': forecast_dates.day
#     })

#     # 예측
#     predicted_values = model.predict(forecast_data)

#     # 예측 결과를 DataFrame으로 반환
#     forecast_df = pd.DataFrame({
#         '날짜': forecast_dates,
#         '예측 환율': predicted_values
#     })

#     # 선택된 나라에 대한 예측 결과 반환
#     forecast_df['currency'] = selected_country_code

#     # 인덱스 리셋
#     forecast_df.reset_index(drop=True, inplace=True)

#     return forecast_df

# # 메인 함수
# def main():
#     # 사용자 입력 받기
#     selected_country_code, selected_date = get_user_input()

#     # 크롤링 시작 날짜와 끝 날짜 설정
#     search_finish_date = selected_date
#     search_start_date = search_finish_date - datetime.timedelta(days=365 * 5)

#     # 전체 데이터 크롤링 (예시)
#     df = pd.DataFrame(crawl_exchange_rate_data(search_start_date, search_finish_date, selected_country_code))

#     if df.empty:
#         st.write("해당 기간의 환율 데이터가 없습니다.")
#         return

#     # 모델 학습
#     model = train_model(df)

#     # 예측된 환율 추출
#     forecast_df = predict_exchange_rate(model, selected_date, search_finish_date, selected_country_code)

#     # 예측된 환율 중에서 최저 5개를 오름차순으로 선택
#     lowest_5 = forecast_df.nsmallest(5, '예측 환율')  # 오름차순으로 선택

#     # 예측 결과 표시
#     st.write(f"{country_dict[selected_country_code]} ({selected_country_code})의 환율 예측:")
#     st.write(lowest_5[['날짜', '예측 환율']])


# if __name__ == "__main__":
#     main()


### 최종
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
with open('C:/ITStudy/4WU/exchange-rate-analysis/pages/country.json', 'r', encoding='utf-8') as f:
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

# import json
# import requests
# import pandas as pd
# import datetime
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# import streamlit as st
# from sklearn.model_selection import GridSearchCV
# from bs4 import BeautifulSoup

# # country.json 파일 읽기
# with open('C:/ITStudy/4WU/exchange-rate-analysis/pages/country.json', 'r', encoding='utf-8') as f:
#     country_dict = json.load(f)

# # 모든 통화 코드 리스트
# currencies = list(country_dict.keys())

# # 사용자 입력 받기 (통화 코드와 날짜)
# def get_user_input():
#     selected_country = st.selectbox("나라를 선택하세요:", list(country_dict.values()))
#     selected_date = st.date_input("여행 날짜를 선택하세요:", datetime.date.today() + datetime.timedelta(days=10))  # 기본 10일 후
#     selected_country_code = [key for key, value in country_dict.items() if value == selected_country][0]
#     return selected_country_code, selected_date

# # WooriBank API로 환율 데이터 크롤링 (최적화)
# def crawl_exchange_rate_data(start_date, end_date, currency_code):
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
#     }

#     # 날짜 범위에 맞게 API 요청하기
#     body = {
#         'BAS_SDT': start_date.strftime('%Y%m%d'),
#         'BAS_EDT': end_date.strftime('%Y%m%d'),
#         'INQ_DIS': currency_code,
#     }

#     url = 'https://spib.wooribank.com/pib/jcc?withyou=CMCOM0185&__ID=c012349'
#     response = requests.post(url, headers=headers, data=body)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # 환율 데이터를 테이블에서 추출
#     trs = soup.select('#resultArea_601_02_01 > table > tbody > tr')
    
#     exchange_rate_by_date = []
#     for tr in trs:
#         tds = tr.find_all('td')
#         date = datetime.datetime.strptime(tds[0].get_text(), '%Y.%m.%d')  # 첫 번째 <td>에서 날짜 추출
#         trading_base_rate = tds[5].get_text(strip=True).replace(',', '')  # 여섯 번째 <td>에서 환율 추출, 쉼표 제거
#         try:
#             exchange_rate_by_date.append({
#                 'date': date,
#                 'currency': currency_code,
#                 'exchange_rate': float(trading_base_rate)
#             })
#         except ValueError:
#             continue  # 환율이 숫자가 아닌 경우 예외 처리
    
#     # 중복된 날짜 제거 (시간 절약)
#     df = pd.DataFrame(exchange_rate_by_date)
#     df = df.drop_duplicates(subset=['date'], keep='last')
#     return df

# # 하이퍼파라미터 튜닝 함수
# def tune_hyperparameters(df):
#     df['date'] = pd.to_datetime(df['date'])
#     df['day_of_year'] = df['date'].dt.dayofyear
#     df['year'] = df['date'].dt.year
#     df['month'] = df['date'].dt.month
#     df['weekday'] = df['date'].dt.weekday  # 요일 추가
#     df['is_weekend'] = (df['weekday'] >= 5).astype(int)  # 주말 여부 추가

#     df['exchange_rate'] = df['exchange_rate'].astype(float)

#     features = ['day_of_year', 'year', 'month', 'weekday', 'is_weekend']
#     target = 'exchange_rate'

#     X = df[features]
#     y = df[target]

#     # 하이퍼파라미터 그리드 정의
#     param_grid = {
#         'n_estimators': [100, 200, 300],
#         'max_depth': [5, 10, 15, None],
#         'min_samples_split': [2, 5, 10],
#         'min_samples_leaf': [1, 2, 4],
#         'bootstrap': [True, False]
#     }

#     # GridSearchCV 설정
#     grid_search = GridSearchCV(estimator=RandomForestRegressor(random_state=42),
#                                param_grid=param_grid,
#                                cv=5,
#                                n_jobs=-1,
#                                verbose=2)

#     # GridSearchCV 모델 학습
#     grid_search.fit(X, y)

#     # 최적의 하이퍼파라미터 출력
#     # st.write("최적의 하이퍼파라미터:", grid_search.best_params_)

#     return grid_search.best_estimator_

# # 모델 학습 함수 (하이퍼파라미터 튜닝 포함)
# def train_model_with_tuning(df):
#     best_model = tune_hyperparameters(df)
#     return best_model

# # 예측 함수 (최적화)
# def predict_exchange_rate(model, start_date, end_date):
#     forecast_dates = pd.date_range(start=start_date, end=end_date, freq='D')
#     forecast_data = pd.DataFrame({
#         'day_of_year': forecast_dates.dayofyear,
#         'year': forecast_dates.year,
#         'month': forecast_dates.month,
#         'weekday': forecast_dates.weekday,
#         'is_weekend': (forecast_dates.weekday >= 5).astype(int)
#     })

#     # 예측 (벡터화로 처리)
#     predicted_values = model.predict(forecast_data)

#     forecast_df = pd.DataFrame({
#         '날짜': forecast_dates,
#         '예측 환율': predicted_values
#     })

#     return forecast_df

# # 성능 평가 함수
# def evaluate_model(model, df):
#     X = df[['day_of_year', 'year', 'month', 'weekday', 'is_weekend']]
#     y_true = df['exchange_rate']

#     # 예측
#     y_pred = model.predict(X)

#     # 성능 평가
#     mae = mean_absolute_error(y_true, y_pred)
#     mse = mean_squared_error(y_true, y_pred)
#     r2 = r2_score(y_true, y_pred)

#     return mae, mse, r2

# # 메인 함수
# def main():
#     # 사용자 입력 받기
#     selected_country_code, selected_date = get_user_input()

#     # 크롤링 시작 날짜와 끝 날짜 설정
#     today_date = datetime.date.today()
#     search_finish_date = selected_date
#     search_start_date = today_date - datetime.timedelta(days=365 * 5)  # 5년치 데이터

#     # 전체 데이터 크롤링
#     df = crawl_exchange_rate_data(search_start_date, search_finish_date, selected_country_code)

#     if df.empty:
#         st.write("해당 기간의 환율 데이터가 없습니다.")
#         return

#     # 모델 학습 (하이퍼파라미터 튜닝 포함)
#     model = train_model_with_tuning(df)

#     # 예측된 환율 추출
#     forecast_df = predict_exchange_rate(model, today_date, selected_date)

#     # 예측된 환율 중에서 최저 2개를 오름차순으로 선택
#     lowest_2 = forecast_df.nsmallest(2, '예측 환율')  # 오름차순으로 선택

#     # 예측 결과 표시
#     st.write(f"{country_dict[selected_country_code]} ({selected_country_code})의 환율 예측:")
#     st.write(lowest_2[['날짜', '예측 환율']])

#     # 성능 평가
#     mae, mse, r2 = evaluate_model(model, df)

#     st.write(f"모델 성능 평가:", font_size=15)
#     st.write(f"MAE (평균 절대 오차): {mae:.2f}", font_size=15)
#     st.write(f"MSE (평균 제곱 오차): {mse:.2f}", font_size=15)
#     st.write(f"R2 (결정 계수): {r2:.2f}", font_size=15)


# if __name__ == "__main__":
#     main()
