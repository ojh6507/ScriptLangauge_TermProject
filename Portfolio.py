from server import *
import stock_search

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
        self.window = Toplevel(root)
        self.window.title('포트폴리오')
        self.window.geometry('420x310')
        self.window.configure(bg='white')
        self.portfolio_listbox = Listbox(self.window,width=40)
        self.portfolio_listbox.pack(padx=20, pady=20)
        self.add_button = Button(self.window, text="추가",font=("Arial",8,"bold"),activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', command=self.add_stock)
        self.add_button.place(x=220, y=190, width=32, height=30)
      
        self.sav_button = Button(self.window, text="저장",font=("Arial",8,"bold"),activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', command=self.save_stocks)
        self.sav_button.place(x=260, y=190, width=32, height=30)
        self.sav_button = Button(self.window, text="불러오기",font=("Arial",8,"bold"),activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', command=self.load_stocks)
        self.sav_button.place(x=300, y=190, width=52, height=30)

        self.window.mainloop()
    

    def set_data(self):
        if self.ticker:
            code = self.ticker[:-3]
            temp2 = self.get_price(code)
            self.current_price = int(temp2['stck_prpr'])
          

    def on_result_select(self):
        self.selected_index = self.results_listbox.curselection()
        self.initBuy = False
        if self.selected_index:
            self.key = self.results_listbox.get(self.selected_index[0])
            self.stock_name_blank.delete(0, END)  # 기존 텍스트 삭제
            self.stock_name_blank.insert(0, self.key)  # 새로운 텍스트 삽입
            self.ticker = self.results[self.key]

            self.set_data()
            
            self.search_results_window.destroy()

    def confirm(self):
        pass
    
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
        sub_window = Toplevel(self.window)
        sub_window.title('주식 추가')
        sub_window.geometry('280x150')
        sub_window.configure(bg='white')
        stock_name_label = Label(sub_window,text = '종목명: ',bg='white',font=("Arial",11,"bold"))
        stock_name_label.place(x=10, y=10, w=100,h=20)
        self.stock_name_blank = Entry(sub_window)
        self.stock_name_blank.place(x=100, y=10, w=100,h=20)

        searchB = Button(sub_window,text='검색',font=("Arial",10,"bold") ,activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', 
                         command= self.show_search_results)
        searchB.place(x=205, y=10, w=40,h=25)

        stock_price_label = Label(sub_window,font=("Arial",11,"bold"),bg='white',text = '매입가: ')
        stock_price_label.place(x=10, y=50, w=100,h=20)
        stock_price_blank = Entry(sub_window)
        stock_price_blank.place(x=100, y=50, w=100,h=20)
        
        stock_count_label = Label(sub_window,font=("Arial",11,"bold"),bg='white' ,text = '수량: ')
        stock_count_label.place(x=10, y=90, w=100,h=20)
        stock_count_blank = Entry(sub_window)
        stock_count_blank.place(x=100, y=90, w=100,h=20)
        
        confirmB = Button(sub_window,text='확인',font=("Arial",11,"bold") ,activeforeground='#BDBDBD',activebackground='#303F9F',fg='#FFFFFF',bg='#3F51B5', command=self.confirm)
        confirmB.place(x=-55,y=120,w=400,h=30)
        sub_window.mainloop()
        pass
    def save_stocks(self):
        pass
    def load_stocks(self):
        pass


if __name__ == '__main__':
    root = Tk()
    portfolio(root)