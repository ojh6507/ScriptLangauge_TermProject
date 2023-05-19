from server import *
from bollinger_bands import *
from stock_search import*

matplotlib.use("TkAgg")
yf.pdr_override()
supported_intervals = ["1d", "5d", "1wk", "1mo", "3mo"]
ticker = ''
class BBMain:
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

    def show_search_results(self):
        global ticker
        if self.results:
            if self.market.get() == 'Nasdaq':
                self.search_results_window = Toplevel(self.root)
                self.search_results_window.title("검색 결과")
                self.results_listbox = Listbox(self.search_results_window, selectmode=SINGLE)
                
                for result in self.results:
                    self.results_listbox.insert(END, result)

                self.results_listbox.pack(padx=20, pady=20)
                select_button = Button(self.search_results_window, text="선택", command = self.on_result_select)
                select_button.pack(padx=20, pady=20)

            elif self.market.get() == 'Kor':
                if isinstance(self.results,list):
                    ticker = self.results[0]
                    self.update_chart_thread()

                elif isinstance(self.results, dict):
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
        else:
            self.action_label.config(text="검색 결과를 찾을 수 없습니다.")
    
    def on_result_select(self):
        global ticker
        self.selected_index = self.results_listbox.curselection()
        if self.selected_index:
            if isinstance(self.results, dict):
                key = self.results_listbox.get(self.selected_index[0])
                ticker = self.results[key]
            else:
                ticker = self.results[self.selected_index[0]]
            self.search_results_window.destroy()
            self.update_chart_thread()
    
    def search_stock(self):
        if self.market.get():
            self.fig.clf()
            self.gfig.clf()
            self.rsi_fig.clf()
            self.action_label.config(text="현재 주가에 대한 추천: ")
            self.gcanvas.draw()
            self.canvas.draw()
            company_name = self.company_entry.get()
            self.results = search_tickers_by_name(self.market.get(), company_name)
            if self.results:
                self.show_search_results()
            else:
                self.action_label.config(text="검색 결과를 찾을 수 없습니다.")
        else:
                self.action_label.config(text="주식 시장을 선택해주세요")


    def update_chart_thread(self):
        if self.currentTab == 'RSI':
            update_thread= threading.Thread(target=self.update_rsi_chart)
        else:
            update_thread = threading.Thread(target=self.update_chart)
        update_thread.start()

    def show_loading_screen(self):
        loading_screen = Toplevel(self.root)
        loading_screen.title("Loading...")
        loading_label = Label(loading_screen, text="데이터를 로드하는 중입니다. 잠시 기다려 주세요...")
        loading_label.pack(padx=20, pady=20)

        progressbar = ttk.Progressbar(loading_screen, mode="indeterminate")
        progressbar.pack(padx=20, pady=20)
        progressbar.start()
        progressbar.update()

        loading_screen.lift()
        self.root.attributes("-disabled", True)
        self.root.update()  # Change this line

        return loading_screen, progressbar

    def hide_loading_screen(self,loading_screen, progressbar):
        progressbar.stop()
        self.root.attributes("-disabled", False)
        loading_screen.destroy()


    def get_default_window(self, interval):
        if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
            return 20
        elif interval in ["1d", "5d"]:
            return 20
        elif interval == "1wk":
            return 4
        elif interval in ["1mo", "3mo"]:
            return 3
        else:
            return 20


    def update_chart(self):
        global ticker
        if ticker!='':
            loading_screen, progressbar = self.show_loading_screen()
            self.root.update()

            interval = self.interval_var.get()
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            window = self.window_var.get()

            stock_data = download_stock_data(ticker, start_date, end_date, interval)
         
            stock_data = calculate_bollinger_bands(stock_data, window)
                # Get company name
            self.stock_ticker = yf.Ticker(ticker)
            company_info = self.stock_ticker.info
            company_name = company_info.get('shortName', ticker)

            if not stock_data.empty:
              
                if self.currentTab == '볼린저밴드':
                    action = analyze_bollinger_bands(stock_data)
                    self.action_label.config(text=f"현재 주가에 대한 추천: {action}")
                    ax = self.fig.add_subplot(111)
                    
                    ax.plot(stock_data.index, stock_data['Close'], label='Close', color='blue')
                    ax.plot(stock_data.index, stock_data['Moving Average'], label='Moving Average', color='red')
                    ax.plot(stock_data.index, stock_data['Upper Band'], label='Upper Band', color='green')
                    ax.plot(stock_data.index, stock_data['Lower Band'], label='Lower Band', color='orange')
                    ax.fill_between(stock_data.index, stock_data['Lower Band'], stock_data['Upper Band'], color='gray', alpha=0.2)
                    ax.set_title(f"{company_name} Bollinger Bands")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Price")
                    ax.legend(loc="best")
                    
                else:
                    self.gfig.clf()
                    ax2 = self.gfig.add_subplot(111)

                    # Assuming 'Date' is the index of stock_data
                    ohlc_data = stock_data[['Open', 'High', 'Low', 'Close']].copy()

                    # Reset index and convert 'Date' to numerical format
                    ohlc_data = ohlc_data.reset_index()
                    ohlc_data['Date'] = pd.to_datetime(ohlc_data['Date'])
                    ohlc_data['Date'] = ohlc_data['Date'].map(mdates.date2num)

                    candlestick_ohlc(ax2, ohlc_data.values, width=0.6, colorup='g', colordown='r')
                    ax2.xaxis_date()
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                    ax2.set_title(f"{company_name} Candlestick Chart")
                    ax2.set_xlabel("Date")
                    ax2.set_ylabel("Price")
            else:
                 self.action_label.config(text="주가 데이터를 찾을 수 없습니다.")
            
            self.hide_loading_screen(loading_screen, progressbar) 
            self.canvas.draw()
            self.gcanvas.draw()

    def update_window(self, *args):
        interget = self.interval_var.get()
        default_window = self.get_default_window(interget)
        self.window_var.set(default_window)

    def __init__(self,master):
        self.root = Toplevel(master)
        self.root.title("Stock Analyzer")
        
        #탭 추가
        self.notebook = ttk.Notebook(self.root)
        self.graph_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_tab, text='캔들스틱 차트')

        self.gfig = plt.figure(figsize=(12, 6))
        self.gcanvas = FigureCanvasTkAgg(self.gfig, master=self.graph_tab)
        self.gcanvas.get_tk_widget().pack()

        # 볼린저밴드 탭
        self.bb_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.bb_tab, text='볼린저밴드')
       
          # RSI 탭 추가
        self.rsi_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.rsi_tab, text='RSI')
        self.rsi_fig = plt.figure(figsize=(12, 6))
        self.rsi_canvas = FigureCanvasTkAgg(self.rsi_fig, master=self.rsi_tab)
        self.rsi_canvas.get_tk_widget().pack()
       

        self.interval_var = StringVar( self.root)
        self.interval_var.set("1d")  # default value
        self.interval_var.trace("w", self.update_window)

        self.interval_optionmenu = OptionMenu(self.root, self.interval_var, *supported_intervals)
        
        self.window_var = IntVar(self.root)
        self.window_var.set(20)  # default value

        self.company_label = Label(self.root, text="회사 이름:")
        self.company_label.pack()
        self.company_entry = Entry(self.root)
        self.company_entry.pack()

        self.search_button = Button(self.root, text="검색", command=self.search_stock)
        self.search_button.place(x=680, y=20, width=50, height=20)
      
        self.market = StringVar(self.root,value ='Kor')
        Nasdaq_bt = Radiobutton(self.root, text="나스닥",value = 'Nasdaq',variable=self.market,  command=  self.ChangeMarket)
        Nasdaq_bt.pack()
        korea_bt = Radiobutton(self.root, text="코스피/코스닥",value = 'Kor', variable=self.market, command= self.ChangeMarket)
        korea_bt.pack()
       
        
        self.window_label = Label(self.root, text="이동 평균 기간 선택:")
        self.window_label.pack()
        window_spinbox = Spinbox(self.root, from_=1, to=100, textvariable=self.window_var)
        window_spinbox.pack()
        self.interval_label = Label(self.root, text="주기 선택:")
        self.interval_label.place(x=470, y=138, width=100, height=20)
        self.interval_optionmenu.pack()
      
        update_button = Button(self.root, text="차트 업데이트",font=("Arial", 15), command=self.update_chart_thread)
        update_button.place(x=1000, y=15, width=150, height=130)

        self.notebook.pack(expand=1, fill='both')
        self.action_label = Label(self.root, text="현재 주가에 대한 추천: ", font=("Arial", 15))
        self.action_label.place(x=0, y=50, width=300, height=40)
        self.market_label = Label(self.root, text="Stock Market : KOSPI / KOSDAQ", font=("Arial", 13))
        self.market_label.place(x=20, y=100, width=300, height=40)

        self.fig = plt.figure(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.bb_tab)
        self.canvas.get_tk_widget().pack()
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.on_window_close(self.root))
        self.currentTab = '그래프'
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.update_chart()

        self.root.mainloop()

    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "그래프":
            self.currentTab ='그래프'
          
        elif selected_tab == "볼린저밴드":
            self.currentTab = '볼린저밴드'
        elif selected_tab == 'RSI':
            self.currentTab ='RSI'
         
            
    def ChangeMarket(self):
       
       if self.market.get() == 'Kor':
           self.market_label.config ( text= "Stock Market : KOSPI / KOSDAQ")
       else:
           self.market_label.config ( text= "Stock Market : NASDAQ")
    
    def calculate_RSI(self, data, time_window):
        diff = data.diff(1).dropna()        # diff in one field(one day)

        # positive gains (up) and negative gains (down) Series
        up, down = diff.copy(), diff.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        
        # EMAs of ups and downs
        roll_up = up.ewm(span=time_window).mean()
        roll_down = down.abs().ewm(span=time_window).mean()

        # Relative Strength (RS)
        RS = roll_up / roll_down

        # Relative Strength Index (RSI)
        RSI = 100.0 - (100.0 / (1.0 + RS))
        return RSI
    
    def get_action_based_on_rsi(self):
        if self.rsi < 30:
            return "매수"
        elif self.rsi > 70:
            return "매도"
        else:
            return "관망"
    
    def update_rsi_chart(self):
        # RSI 그래프 업데이트 메소드
        if(ticker):
            loading_screen, progressbar = self.show_loading_screen()
            self.root.update()
            interval = self.interval_var.get()  # 시간 간격
           
            # fetch data
            data = yf.download(ticker, period='1y', interval=interval)
            stock_info = yf.Ticker(ticker)
            company_info =  stock_info.info
            company_name = company_info.get('shortName', ticker)

            data['RSI'] = self.calculate_RSI(data['Close'], 14)
            self.rsi =  data['RSI'].iloc[-1]

            self.rsi_fig.clear()
            ax = self.rsi_fig.add_subplot(111)
            ax.plot(data.index, data['RSI'], label= company_name + ' RSI', color='lightblue')
            ax.axhline(0, color='gray', linewidth=2)
            ax.axhline(30, color='red', linestyle='--')
            ax.axhline(70, color='red', linestyle='--')
            ax.axhline(100, color='gray', linewidth=2)
            ax.legend(loc='best')

            action = self.get_action_based_on_rsi()
            self.action_label.config(text=f"현재 주가에 대한 추천: {action}")
            self.hide_loading_screen(loading_screen, progressbar) 
            self.rsi_canvas.draw()
    # 창 종료 이벤트 처리 함수
    def on_window_close(self, root):
        global ticker
        ticker =''
        root.quit()
        root.destroy()
