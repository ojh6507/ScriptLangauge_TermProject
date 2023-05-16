from server import *

# 주식 데이터 다운로드
def download_stock_data(ticker, start, end, interval):
    stock_data = pdr.get_data_yahoo(ticker, start=start, end=end, interval=interval)
    return stock_data

def calculate_bollinger_bands(stock_data, window=20, k=2):
    stock_data['Moving Average'] = stock_data['Close'].rolling(window=window).mean()
    stock_data['Standard Deviation'] = stock_data['Close'].rolling(window=window).std()
    stock_data['Upper Band'] = stock_data['Moving Average'] + (stock_data['Standard Deviation'] * k)
    stock_data['Lower Band'] = stock_data['Moving Average'] - (stock_data['Standard Deviation'] * k)
    return stock_data

def analyze_bollinger_bands(stock_data):
    last_row = stock_data.iloc[-1]
    last_close_price = last_row['Close']
    last_lower_band = last_row['Lower Band']
    last_moving_average = last_row['Moving Average']
    
    if last_row['Close'] > last_row['Upper Band']:
        return "매도"
    elif last_row['Close'] < last_row['Lower Band']:
        return "매수"
    elif last_close_price > last_lower_band and last_close_price < last_moving_average:
        # Calculate the slope of the Close price graph
        close_slope = stock_data['Close'].diff().iloc[-1]

        if close_slope > 0:
            return "매수"
        else:
            return "관망"
    else:
        return "관망"



