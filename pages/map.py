import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib3
from datetime import datetime, timedelta
import json
import app


# SSL 경고 무시 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API 키 설정
AUTH_KEY = "zJiQc2Wv8d3mFZJ1OTkLjcphVoFDnSwE"

def get_exchange_rates(search_date):
    """한국수출입은행 환율 API에서 데이터를 가져오는 함수"""
    base_url = 'https://www.koreaexim.go.kr/site/program/financial/exchangeJSON'
    params = {
        'authkey': AUTH_KEY,
        'searchdate': search_date.strftime('%Y%m%d'),
        'data': 'AP01'
    }
    
    try:
        response = requests.get(base_url, params=params, verify=False)
        
        # HTTP 상태 코드 확인
        if response.status_code != 200:
            st.error(f"API 호출 실패. 상태 코드: {response.status_code}")
            return None
            
        # 응답 내용 확인
        if not response.text:
            st.error("API가 빈 응답을 반환했습니다.")
            return None
            
        try:
            data = response.json()
            if not data:  # 빈 리스트 확인
                #st.warning(f"{search_date.strftime('%Y-%m-%d')} 데이터가 없습니다.")
                return None
            return data
        except json.JSONDecodeError as e:
            st.error(f"JSON 파싱 오류: {str(e)}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 오류: {str(e)}")
        return None

def process_exchange_data(days=7):
    """최근 7일간의 환율 데이터를 수집하고 처리하는 함수"""
    all_data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    current_date = start_date
    while current_date <= end_date:
        data = get_exchange_rates(current_date)
        if data:
            for item in data:
                item['date'] = current_date.strftime('%Y-%m-%d')
                all_data.append(item)
        current_date += timedelta(days=1)
    
    if not all_data:
        st.error("수집된 데이터가 없습니다. API 키를 확인해주세요.")
        return pd.DataFrame()
    
    return pd.DataFrame(all_data)

def analyze_trend(df):
    """국가별 환율 추세를 분석하는 함수"""
    if df.empty:
        return {}
        
    trends = {}
    for country in df['cur_nm'].unique():
        country_data = df[df['cur_nm'] == country].sort_values('date')
        if len(country_data) >= 2:
            try:
                rates = country_data['deal_bas_r'].str.replace(',', '').astype(float)
                trend = 'increase' if rates.iloc[-1] > rates.iloc[0] else 'decrease'
                trends[country] = trend
            except Exception as e:
                st.warning(f"{country} 데이터 처리 중 오류 발생: {str(e)}")
    return trends


currency_to_country = {
    '미국 달러': '미국',
    '일본 엔': '일본',
    '유로': '유로',
    '중국 위안': '중국',
    '영국 파운드': '영국',
    '호주 달러': '호주',
    '캐나다 달러': '캐나다',
    '스위스 프랑': '스위스',
    '스웨덴 크로나': '스웨덴',
    '노르웨이 크로네': '노르웨이',
    '덴마크 크로네': '덴마크',
    '싱가포르 달러': '싱가포르',
    '홍콩 달러': '홍콩',
    '뉴질랜드 달러': '뉴질랜드',
    '말레이시아 링깃': '말레이시아',
    '태국 바트': '태국',
    '베트남 동': '베트남',
    '필리핀 페소': '필리핀',
    '인도 루피': '인도',
    '인도네시아 루피아': '인도네시아',
    '남아프리카공화국 랜드': '남아프리카공화국',
    '터키 리라': '터키',
    '러시아 루블': '러시아',
    '브라질 레알': '브라질',
    '멕시코 페소': '멕시코',
    '사우디아라비아 리얄': '사우디아라비아',
    '아랍에미리트 디르함': '아랍에미리트',
    '이스라엘 세켈': '이스라엘',
    '폴란드 즐로티': '폴란드',
    '헝가리 포린트': '헝가리',
    '체코 코루나': '체코',
    '칠레 페소': '칠레',
    '콜롬비아 페소': '콜롬비아',
    '파키스탄 루피': '파키스탄',
    '이집트 파운드': '이집트',
    '한국 원': '한국'
}


country_to_iso = {
    '미국': 'USA', '일본': 'JPN', '유로': 'EU', '중국': 'CHN',
    '영국': 'GBR', '호주': 'AUS', '캐나다': 'CAN', '스위스': 'CHE',
    '스웨덴': 'SWE', '노르웨이': 'NOR', '덴마크': 'DNK', '싱가포르': 'SGP',
    '홍콩': 'HKG', '뉴질랜드': 'NZL', '말레이시아': 'MYS', '태국': 'THA',
    '베트남': 'VNM', '필리핀': 'PHL', '인도': 'IND', '인도네시아': 'IDN',
    '남아프리카공화국': 'ZAF', '터키': 'TUR', '러시아': 'RUS', '브라질': 'BRA',
    '멕시코': 'MEX', '사우디아라비아': 'SAU', '아랍에미리트': 'ARE',
    '이스라엘': 'ISR', '폴란드': 'POL', '헝가리': 'HUN', '체코': 'CZE',
    '칠레': 'CHL', '콜롬비아': 'COL', '파키스탄': 'PAK', '이집트': 'EGY',
    '한국': 'KOR'
}



def create_scatter_geo_map(trends):
    """국가별 환율 추세를 지도에 표시"""
    if not trends:
        st.error("시각화할 데이터가 없습니다.")
        return None
    
    # trends의 통화 이름을 국가 이름으로 변환
    map_data = []
    for currency, trend in trends.items():
        country = currency_to_country.get(currency)
        if country and country in country_to_iso:
            map_data.append({
                'country': country,
                'iso_alpha': country_to_iso[country],
                'trend': trend
            })
    
    # 데이터프레임 생성
    df_map = pd.DataFrame(map_data)
    
    if df_map.empty:
        st.error("유효한 국가 데이터가 없습니다.")
        return None
    
    # Plotly scatter_geo 생성
    fig = px.scatter_geo(
        df_map,
        locations='iso_alpha',
        color='trend',
        hover_name='country',
        opacity=0.7,
        color_discrete_map={'increase': 'red', 'decrease': 'blue'}
    )
    
    return fig

def main():
    st.title('🌏 세계 환율 변동 추이 지도')
    
    with st.spinner('데이터를 불러오는 중...'):
        # 환율 데이터 수집 및 처리
        df = process_exchange_data()
        
        if not df.empty:
            # 트렌드 분석
            trends = analyze_trend(df)
            
            if trends:
                # 지도 생성
                fig = create_scatter_geo_map(trends)
                if fig:
                    # 지도 표시
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 상세 정보 표시
                    # st.subheader('국가별 환율 변동 추이')
                    # for country, trend in trends.items():
                    #     color = '🔴' if trend == 'increase' else '🔵'
                    #     st.write(f'{color} {country}: {"상승" if trend == "increase" else "하락"} 추세')

if __name__ == '__main__':
    main()
