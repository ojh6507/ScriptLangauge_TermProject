from server import *
from bs4 import BeautifulSoup
import json


def search_companies_naver(name):
    name = urllib.parse.quote(name, encoding='EUC-KR')
    url = f"https://finance.naver.com/search/searchList.naver?query={name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = soup.select(".tbl_search tbody tr")
        companies = {}
        for result in search_results:
            company_name = result.select_one("td.tit > a").text
            company_code = result.select_one("td.tit > a")["href"].split("code=")[-1]

            market_type = result.select_one('td:nth-child(1) > img')['alt'] 
            if market_type =='코스피':  
                category_market = '.KS'
            elif market_type=='코스닥':
                category_market = '.KQ'
            companies[company_name] = company_code + category_market        
        return companies
    else:
        print(f"Error: Server responded with status code {response.status_code}")
        return {}
    
# def search_tiker_by_name_KOR(name):
#     url = f"https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo?serviceKey=tVsU5C%2BXcZFPkfBBZ4FpHvJqtN3FVqAD%2F3nU124LvWj4b%2Bk95RmCUzXhLvK18Acl%2FAA2XP%2B5EeOLQYNz3nJWig%3D%3D&numOfRows=1&itmsNm={name}"

#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, "lxml-xml")

#     isin_cd = soup.find("isinCd")
#     mrkt_Ctg = soup.find("mrktCtg")
#     ticker = ''
#     if isin_cd:
#         print(isin_cd.text)
#         ticker = isin_cd.text[3:9]
    
#         if mrkt_Ctg:
#             if mrkt_Ctg.text =='KOSPI':
#                 ticker +='.KS'
#             elif mrkt_Ctg.text =='KOSDAQ':
#                 ticker += '.KQ'
#         else:
#             print("isinCd 태그를 찾을 수 없습니다.")
#             return None
#     else:
#         print("isinCd 태그를 찾을 수 없습니다.")
#         companies = search_companies_naver(name)
#         return companies
#     return [ticker]



def search_tickers_by_name(market,name):  

    if market == 'Kor':
       return search_companies_naver(name)
    else:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={name}&quotesCount=10&newsCount=0&enableFuzzyQuery=True&quotesQueryId=tss_match_phrase_query&multiQuoteQueryId=multi_quote_single_token_query&newsQueryId=news_ss_symbols&enableCb=true&enableNavLinks=true&enableEnhancedTrivialQuery=true"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        }   
        try:
            Tresult = []
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                for result in data["quotes"]:
                    Tresult.append (result['symbol'])
            else:
                print(f"Error: Server responded with status code {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        return Tresult
    


