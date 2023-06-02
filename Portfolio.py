from server import *
import stock_search
import mock_Stock
APP_KEY = apikey.get_KI_api_key()
APP_SECRET = apikey.get_KI_api_psw()
ACCESS_TOKEN = ''
CANO = apikey.get_CANO()
ACNT_PRDT_CD =apikey.get_ACNT_PRDT_CD()
URL_BASE = apikey.get_URL_Base()

def get_access_token():
    """토큰 발급"""
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":APP_KEY, 
    "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN

class portfolio:
    def __init__(self,root):
        global ACCESS_TOKEN
        ACCESS_TOKEN = get_access_token()
        
        self.stocks = []
        
        self.window = Toplevel(root)
        self.window.title('포트폴리오')
        self.window.geometry('420x310')
        self.window.configure(bg='white')
        self.portfolio_listbox = Listbox(self.window,width=40)
        self.portfolio_listbox.place(x=10, y=20,width=395, height= 180)
        self.add_button = Button(self.window, text="추가",font=("Arial",8,"bold"),activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', command=self.add_stock)
        self.add_button.place(x=220, y=210, width=32, height=30)
      
        self.sav_button = Button(self.window, text="저장",font=("Arial",8,"bold"),activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', command=self.save_stocks)
        self.sav_button.place(x=260, y=210, width=32, height=30)
        self.sav_button = Button(self.window, text="불러오기",font=("Arial",8,"bold"),activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', command=self.load_stocks)
        self.sav_button.place(x=300, y=210, width=52, height=30)
        self.load_init_stocks()
        self.window.mainloop()

    def calculate_profit(self, stock):
        # 현재 가격 구하기
        self.ticker =stock.getTicker()
        self.key = stock.getName()
        self.set_data()
        # 구매 가격 구하기
        purchase_price = stock.get_per_Price()
        # 수익률 계산하기
        profit_rate = (self.current_price - purchase_price) / purchase_price * 100
        return profit_rate
    
    def update_portfolio_listbox(self):
        # 리스트 박스 초기화
        self.portfolio_listbox.delete(0, END)

        # 딕셔너리에 저장된 주식 정보를 리스트 박스에 추가
        for s in self.stocks:
            profit_rate = self.calculate_profit(s) 
            div_money =str(s.getDiv_money())
            div_money = div_money[:-1]
            div_money = div_money.replace(",","")
            
            total_div = int(div_money)*s.getAmount()

            self.portfolio_listbox.insert(END, f"{s.getName()}: {s.get_total_Price()} 원 | {s.getAmount()} 주 | 주당 배당금: {s.getDiv_money()} | 총 배당금:{total_div} 원")

    def set_data(self):
        if self.ticker:
            code = self.ticker[:-3]
            temp2 = self.get_price(code)
            self.current_price = int(temp2['stck_prpr'])
    def update_Div(self,ticker):
        s_ticker = ticker[:-3]
        url = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={s_ticker}&cn="
        # requests 라이브러리를 사용하여 웹 페이지의 HTML을 가져옵니다.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
            }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # BeautifulSoup 객체를 생성하여 HTML을 파싱합니다.
            soup = BeautifulSoup(response.text, 'html.parser')
            datas = soup.find_all('td', {'class': 'num noline-right'})
            sl = []
            for element in datas:
                if '원' in element.get_text():
                    sl.append(element.get_text())
            if sl:
                return sl[-1]
            else:
                return 0
        

                
            

    def confirm(self):
        if self.sl_name and self.ticker and self.stock_price_blank.get() and self.stock_count_blank.get():
            self.total_price = int(self.stock_price_blank.get()) * int(self.stock_count_blank.get())
            s_amount = int(self.stock_count_blank.get())
            div_money = self.update_Div(self.ticker)
            print(div_money)
            self.currentStock = mock_Stock.STOCK(name=self.sl_name, ticker=self.ticker, price=self.total_price //s_amount, amount= s_amount, div_money= div_money)
            self.stocks.append(self.currentStock)
        self.sub_window.destroy()
        self.update_portfolio_listbox()
    


    def on_result_select(self):
        self.selected_index = self.results_listbox.curselection()
        self.initBuy = False
        if self.selected_index:
            self.key = self.results_listbox.get(self.selected_index[0])
            self.stock_name_blank.delete(0, END)  # 기존 텍스트 삭제
            self.stock_name_blank.insert(0, self.key)  # 새로운 텍스트 삽입
            self.sl_name = self.key
            self.ticker = self.results[self.key]

            self.set_data()
            
            self.search_results_window.destroy()

    
    def next_page(self):
        self.start_index += 5
        self.results_listbox.delete(0, END)
        self.display_companies(self.results, self.start_index)

    def prev_page(self):
        if self.start_index > 0:
            self.start_index -= 5
            self.results_listbox.delete(0, END)
            self.display_companies(self.results, self.start_index)

    def display_companies(self, companies, start):
        for i in range(10):
            if start + i < len(companies):
                company_name = list(companies.keys())[start + i]
                self.results_listbox.insert(END, company_name)
            else:
                break
    def get_price(self, code):

        PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
        URL = f"{URL_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
                "authorization": f"Bearer {ACCESS_TOKEN}",
                "appKey":APP_KEY,
                "appSecret":APP_SECRET,
                "tr_id":"FHKST01010100"}
        params = {
        "fid_cond_mrkt_div_code":"J",
        "fid_input_iscd":code,
        }
        res = requests.get(URL, headers=headers, params=params)
        return res.json()['output']

    def show_search_results(self):
        stockName = self.stock_name_blank.get()
        self.results = stock_search.search_companies_naver(stockName)
        if self.results:
            self.search_results_window = Toplevel(self.window)
            self.search_results_window.title("검색 결과")
            self.results_listbox = Listbox(self.search_results_window, selectmode=SINGLE)

            self.start_index = 0
            self.display_companies(self.results, self.start_index)

            self.results_listbox.pack(padx=20, pady=20)

            prev_button = Button(self.search_results_window, text="Prev", command=self.prev_page,fg='#FFFFFF',bg='#3F51B5',)
            prev_button.pack(side=LEFT)

            next_button = Button(self.search_results_window, text="Next", command=self.next_page,fg='#FFFFFF',bg='#3F51B5',)
            next_button.pack(side=RIGHT)

            select_button = Button(self.search_results_window, text="선택", command=self.on_result_select,fg='#FFFFFF',bg='#3F51B5',)
            select_button.pack(padx=20, pady=20)

    def add_stock(self):
        self.sub_window = Toplevel(self.window)
        self.sub_window.title('주식 추가')
        self.sub_window.geometry('280x150')
        self.sub_window.configure(bg='white')
        stock_name_label = Label(self.sub_window,text = '종목명: ',bg='white',font=("Arial",11,"bold"))
        stock_name_label.place(x=10, y=10, w=100,h=20)
        self.stock_name_blank = Entry(self.sub_window)
        self.stock_name_blank.place(x=100, y=10, w=100,h=20)

        searchB = Button(self.sub_window,text='검색',font=("Arial",10,"bold") ,activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', 
                         command= self.show_search_results)
        searchB.place(x=205, y=10, w=40,h=25)

        stock_price_label = Label(self.sub_window,font=("Arial",11,"bold"),bg='white',text = '매입가: ')
        stock_price_label.place(x=10, y=50, w=100,h=20)
        self.stock_price_blank = Entry(self.sub_window)
        self.stock_price_blank.place(x=100, y=50, w=100,h=20)
        
        stock_count_label = Label(self.sub_window,font=("Arial",11,"bold"),bg='white' ,text = '수량: ')
        stock_count_label.place(x=10, y=90, w=100,h=20)
        self.stock_count_blank = Entry(self.sub_window)
        self.stock_count_blank.place(x=100, y=90, w=100,h=20)
        
        confirmB = Button(self.sub_window,text='확인',font=("Arial",11,"bold") ,activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', command=self.confirm)
        confirmB.place(x=-55,y=120,w=400,h=30)
        self.sub_window.mainloop()

    def save_stocks(self):
        pass
    def load_stocks(self):
        pass
     
    def save_stocks(self):
        with open('stocks.pkl', 'wb') as f:
            pickle.dump(self.stocks, f)
            messagebox.showinfo("알림", "저장 완료")

    def load_stocks(self):
        try:
            with open('stocks.pkl', 'rb') as f:
                self.stocks = pickle.load(f)
      
                messagebox.showinfo("알림", "불러오기 완료")
                self.update_portfolio_listbox()
        except FileNotFoundError:
            messagebox.showinfo("알림", "저장된 정보가 없습니다")
    def load_init_stocks(self):
        try:
            with open('stocks.pkl', 'rb') as f:
                self.stocks = pickle.load(f)
                self.update_portfolio_listbox()
        except FileNotFoundError:
            pass
if __name__ == '__main__':
    root = Tk()
    portfolio(root)