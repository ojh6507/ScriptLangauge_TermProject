from server import*
import stock_search
import mock_Stock


client = Client()
APP_KEY = client.get_KoreaInvest_ID()
APP_SECRET = client.get_KoreaInvest_SECRET()
ACCESS_TOKEN = ''
CANO = client.get_CANO()
ACNT_PRDT_CD = client.get_ACNT_PRDT_CD()
URL_BASE = client.get_URL_Base()

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

class MockInvestmentApp:
    def __init__(self,master):
        global ACCESS_TOKEN
        self.root = Toplevel(master)
        self.root.title("주식 모의투자 앱")
        self.root.geometry("475x440")
        ACCESS_TOKEN = get_access_token()
        self.ticker =''
        self.initBuy = False
        self.stocks = [] 
        self.Sellamount = 0
        self.photo = None
        try:
            with open('user.pkl', 'rb') as f:
                self.user = pickle.load(f)
        except FileNotFoundError:
                self.user = mock_Stock.USER()

        self.balance = self.user.getBalance()  # 초기 잔액 설정
        self.create_widgets()
        c = Client()
        self.mapAPIKey = c.get_GoogleMap_KEY()
        self.gmaps = googlemaps.Client(key=self.mapAPIKey)
  
      
    def search_Company_info(self):
        if self.ticker:
            url =  f"https://navercomp.wisereport.co.kr/v2/company/c1020001.aspx?cmp_cd={self.ticker[:-3]}&cn="
            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                td_tag = soup.find('td', {'class': 'txt', 'colspan': '3'})  
                self.loc = td_tag.text.strip()
                self.showMap()
                              
            else:
                print(f"Error: Server responded with status code {response.status_code}")   

    def calculate_buy_total(self):

        self.amount = int(self.stock_buy_amount_entry.get())
        self.set_data()

        self.total_price = self.current_price * self.amount
        if self.total_price > 0:
            self.buy_total_label['text'] = f"{self.amount}주 x {self.current_price}원 : {self.total_price}원"
       
             
    def calculate_Sell_total(self):
        self.Sellamount = int(self.stock_sell_amount_entry.get())
        if  self.amount > self.Sellamount:
            
            self.total_price = self.current_price * self.Sellamount
            self.buy_total_label['text'] = f"{self.Sellamount}주 x {self.current_price}원 : {self.total_price} 원"

            
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

    def buy_stock(self):

        if self.balance - self.total_price > 0:
            self.currentStock = mock_Stock.STOCK(name = self.sl_name, ticker = self.ticker, price= self.total_price // self.amount, amount= self.amount)
            self.balance -= self.total_price

            existing_stock = None
            for stock in self.stocks:
                if stock.getTicker() == self.ticker:
                    existing_stock = stock
                    break
            
            if existing_stock is None:
                self.currentStock = mock_Stock.STOCK(name=self.sl_name, ticker=self.ticker, price=self.total_price // self.amount, amount=self.amount)
                self.stocks.append(self.currentStock)
            else:
                existing_stock.update_amount(self.amount)

            self.update_portfolio_listbox()
            self.update_sell_option_menu()
        # 새로 추가된 메소드 호출
        else:
            messagebox.showinfo("Error", "잔액이 부족합니다")
        self.balance_label['text'] = f"잔액: {self.balance} 원"
  
    def sell_stock(self):
        # 선택한 주식의 ticker
        self.set_data()
        self.stockName = self.sell_stock_var.get()
        existing_stock = None
        for stock in self.stocks:
            if stock.getTicker() == self.ticker:
                existing_stock = stock
                break

        if existing_stock.getAmount() >= self.Sellamount:
            existing_stock.update_Sell_amount(self.Sellamount)
            if existing_stock.getAmount() == 0:
                del existing_stock 
            # 매도한 주식의 가격을 잔액에 추가
            total_price = int(self.current_price) * self.Sellamount
            self.balance += total_price
            # 잔액 업데이트
            self.balance_label['text'] = f"잔액: {self.balance} 원"

            # 매도 옵션 메뉴 업데이트
            self.update_sell_option_menu()
            self.update_portfolio_listbox()
        else:
            messagebox.showinfo("Error", "판매할 주식이 부족합니다.")
    
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
    
    '''포트폴리오 업데이트'''
    def update_portfolio_listbox(self):
        # 리스트 박스 초기화
        self.portfolio_listbox.delete(0, END)

        # 딕셔너리에 저장된 주식 정보를 리스트 박스에 추가
        for s in self.stocks:
            profit_rate = self.calculate_profit(s) 
            self.portfolio_listbox.insert(END, f"{s.getName()}: {s.get_total_Price()} 원 | {s.getAmount()} 주 | 수익률: {profit_rate:.2f}%")
    def update_sell_option_menu(self):
        # 메뉴 초기화
        self.sell_stock_option['menu'].delete(0, 'end')
        # 사용자가 보유한 주식 종목 추가
        for ticker in self.stocks:
            self.sell_stock_option['menu'].add_command(label=ticker.getName(), command=lambda t=ticker.getName(): self.sell_stock_var.set(t))
    
    '''위젯 생성'''
    def create_widgets(self):
          # Notebook 생성
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        # 주식 검색 탭
        self.stock_search_frame = Frame(self.notebook)
        self.notebook.add(self.stock_search_frame, text="메인 메뉴")
        # 포트폴리오 탭
        self.portfolio_frame = Frame(self.notebook)
        self.notebook.add(self.portfolio_frame, text="포트폴리오")
        # 포트폴리오 Frame
        self.portfolio_listbox = Listbox(self.portfolio_frame,width=40)
        self.portfolio_listbox.pack(padx=20, pady=20)
        self.sav_button = Button(self.portfolio_frame, text="저장", command=self.save_stocks)
        self.sav_button.place(x=290, y=200, width=30, height=30)
        self.sav_button = Button(self.portfolio_frame, text="불러오기", command=self.load_stocks)
        self.sav_button.place(x=330, y=200, width=50, height=30)

        #검색 frame
        self.sell_stock_var = StringVar(self.stock_search_frame)
        self.sell_stock_option = OptionMenu(self.stock_search_frame, self.sell_stock_var, [])
        self.sell_stock_option.place(x=200, y=320, width=100, height=20)
        self.update_sell_option_menu()  # 새로 추가된 메소드 호출
        self.search_stock_label = Label(self.stock_search_frame, text="주식 검색:")
        self.search_stock_label.place(x=5, y=30, width=100, height=14)
        self.stock_name_entry = Entry(self.stock_search_frame)
        self.stock_name_entry.place(x=150, y=30, width=150, height=20)
        self.search_button = Button(self.stock_search_frame, text="검색", command=self.search_stock)
        self.search_button.place(x=350, y=10, width=100, height=100)
        self.refresh_button = Button(self.stock_search_frame, text="새로고침", command=self.set_data)
        self.refresh_button.place(x=350, y=140, width=100, height=30)
        
        self.show_Loc_button = Button(self.stock_search_frame, text="기업 위치", command=self.search_Company_info)
        self.show_Loc_button.place(x=20, y=140, width=100, height=30)
        

        self.stocks_label = Label(self.stock_search_frame, text="검색결과:")
        self.stocks_label.place(x=0, y=100, width=100, height=20)

        self.stocks_name = Label(self.stock_search_frame, text="")
        self.stocks_name.place(x=140, y=80, width=130, height=20)
        self.stock_curr_label = Label(self.stock_search_frame, text="")
        self.stock_curr_label.place(x=150, y=100, width=110, height=20)
        self.stock_open_label = Label(self.stock_search_frame, text="")
        self.stock_open_label.place(x=150, y=120, width=110, height=20)
        self.stock_high_label = Label(self.stock_search_frame, text="")
        self.stock_high_label.place(x=150, y=140, width=110, height=20)
        self.stock_lower_label = Label(self.stock_search_frame, text="")
        self.stock_lower_label.place(x=150, y=160, width=110, height=20)
     
        # 모의 투자
        self.balance_label = Label(self.stock_search_frame, text=f"잔액: {self.balance} 원")
        self.balance_label.place(x=10, y=210, width=100, height=20)        
        self.buy_stock_button = Button(self.stock_search_frame, text="매수", command= self.buy_stock)
        self.buy_stock_button.place(x=350, y=210, width=100, height=100)
        self.sell_stock_button = Button(self.stock_search_frame, text="매도", command=self.sell_stock)
        self.sell_stock_button.place(x=350, y=320, width=100, height=100)  
        self.buy_label = Label(self.stock_search_frame, text="매수 수량 :")

        self.buy_label.place(x=50, y=240, width=100, height=20)        
        self.stock_buy_amount_entry = Entry(self.stock_search_frame)
        self.stock_buy_amount_entry.place(x=150, y=240, width=150, height=20)
        self.buy_confirm_button = Button(self.stock_search_frame, text="확인", command=self.calculate_buy_total)
        self.buy_confirm_button.place(x=305, y=235, width=30, height=30)
        self.buy_total_label = Label(self.stock_search_frame, text="")
        self.buy_total_label.place(x=150, y=270, width=170, height=20)


        self.sell_label = Label(self.stock_search_frame, text="매도 수량 :")
        self.sell_label.place(x=50, y=360, width=100, height=20)        
        self.stock_sell_amount_entry = Entry(self.stock_search_frame)
        self.stock_sell_amount_entry.place(x=150, y=360, width=150, height=20)
        self.sell_confirm_button = Button(self.stock_search_frame, text="확인", command=self.calculate_Sell_total)
        self.sell_confirm_button.place(x=305, y=355, width=30, height=30)

        XLine = Canvas(self.stock_search_frame, width=470, height=1, bg='black')
        XLine.place(x=0, y=1)
        XLine = Canvas(self.stock_search_frame, width=470, height=1, bg='black')
        XLine.place(x=0, y=200)
      
        XLine = Canvas(self.stock_search_frame, width=470, height=1, bg='black')
        XLine.place(x=0, y=430)
        YLine = Canvas(self.stock_search_frame, width=1, height=430, bg='black')
        YLine.place(x= 470, y= 0)
        YLine = Canvas(self.stock_search_frame, width=1, height=430, bg='black')
        YLine.place(x= 1, y= 0)
        self.search_stock_label = Label(self.stock_search_frame, text="주식 검색:")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
    
  
    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "포트폴리오":
            self.update_portfolio_listbox()




    '''모의투자 포트폴리오 저장'''
    def save_stocks(self):
        with open('stocks.pkl', 'wb') as f:
            self.user.set_balance(self.balance)
            pickle.dump(self.stocks, f)
        with open('user.pkl', 'wb') as f:
            pickle.dump(self.user,f)
            messagebox.showinfo("알림", "저장 완료")

    def load_stocks(self):
        try:
            with open('stocks.pkl', 'rb') as f:
                self.stocks = pickle.load(f)
      
                messagebox.showinfo("알림", "불러오기 완료")
        except FileNotFoundError:
            messagebox.showinfo("알림", "저장된 정보가 없습니다")

    def display_companies(self, companies, start):
        for i in range(10):
            if start + i < len(companies):
                company_name = list(companies.keys())[start + i]
                self.results_listbox.insert(END, company_name)
            else:
                break


    def next_page(self):
        self.start_index += 5
        self.results_listbox.delete(0, END)
        self.display_companies(self.results, self.start_index)

    def prev_page(self):
        if self.start_index > 0:
            self.start_index -= 5
            self.results_listbox.delete(0, END)
            self.display_companies(self.results, self.start_index)
    
    def showMap(self):
        mapWindow = Toplevel(self.root)

        mapWindow.title('기업위치')
        if self.loc:
            geocode_result = self.gmaps.geocode(self.loc)[0]
            lat = geocode_result['geometry']['location']['lat']
            lng = geocode_result['geometry']['location']['lng']

            # Google Static Maps API에 마커를 추가
            url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom=11&size=400x400&maptype=roadmap&markers=color:red%7Clabel:C%7C{lat},{lng}"
            response = requests.get(url+'&key='+self.mapAPIKey)
            image = PILImage.open(io.BytesIO(response.content))
            self.photo = ImageTk.PhotoImage(image)

            # 이미지를 표시하는 레이블을 생성하고 이를 윈도우에 배치
            map_label = Label(mapWindow, image=self.photo)
            map_label.pack()
            
    def show_search_results(self):
        stockName =  self.stock_name_entry.get()
        self.results = stock_search.search_companies_naver(stockName)
        if self.results:
            self.search_results_window = Toplevel(self.root)
            self.search_results_window.title("검색 결과")
            self.results_listbox = Listbox(self.search_results_window, selectmode=SINGLE)

            self.start_index = 0
            self.display_companies(self.results, self.start_index)

            self.results_listbox.pack(padx=20, pady=20)

            prev_button = Button(self.search_results_window, text="Prev", command=self.prev_page)
            prev_button.pack(side=LEFT)

            next_button = Button(self.search_results_window, text="Next", command=self.next_page)
            next_button.pack(side=RIGHT)

            select_button = Button(self.search_results_window, text="선택", command=self.on_result_select)
            select_button.pack(padx=20, pady=20)
      

    
    def on_result_select(self):
        self.selected_index = self.results_listbox.curselection()
        self.initBuy = False
        if self.selected_index:
            self.key = self.results_listbox.get(self.selected_index[0])
            self.ticker = self.results[self.key]

            self.set_data()
            
            self.search_results_window.destroy()


    def show_Select_INFO(self,name):
        
        self.stocks_name['text'] = name
        self.sl_name = name
        self.stock_curr_label['text'] = f'현재가: {self.current_price} 원'
        self.stock_open_label['text'] = f'시가: {self.open_price} 원'
        self.stock_high_label['text'] = f'고가: {self.high_price} 원'
        self.stock_lower_label['text'] = f'저가: {self.lower_price} 원'
       

    def set_data(self):
        code = self.ticker[:-3]
        temp2 = self.get_price(code)
        self.current_price = int(temp2['stck_prpr'])
        self.open_price =  int(temp2['stck_oprc'])
        self.high_price = int(temp2['stck_hgpr'])
        self.lower_price = int(temp2['stck_lwpr'])
        self.show_Select_INFO(self.key)
    
        
    
    def search_stock(self):
        self.show_search_results()


if __name__ == "__main__":
    app = MockInvestmentApp()