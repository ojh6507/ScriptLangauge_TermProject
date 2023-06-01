from telegram import *
from telegram.ext import *
from stock_search import *
from server import*
token=apikey.get_Telegram_KEY()
#tukorea_stock_bot
SELECT_COMPANY = 1
compnay_dict = {}


APP_KEY = apikey.get_KI_api_key()
APP_SECRET = apikey.get_KI_api_psw()
ACCESS_TOKEN = ''
CANO = apikey.get_CANO()
ACNT_PRDT_CD =apikey.get_ACNT_PRDT_CD()
URL_BASE = apikey.get_URL_Base()

def get_access_token():
    global ACCESS_TOKEN
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

def get_price(code):
        global ACCESS_TOKEN
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

def set_data(company_value) ->int:
        code = company_value[:-3]
        temp2 = get_price(code)
        current_price = int(temp2['stck_prpr'])
        open_price =  int(temp2['stck_oprc'])
        high_price = int(temp2['stck_hgpr'])
        lower_price = int(temp2['stck_lwpr'])
        message = f"현재 가격: {current_price}\n시가: {open_price}\n고가: {high_price}\n저가: {lower_price}"
        return message

def echo(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    global company_dict
    # 기업 목록 가져오기
    company_dict = search_companies_naver(text)
    company_names = list(company_dict.keys())

    if not company_names:
        update.message.reply_text('No companies found.')
        return

    # 인라인 키보드 생성
    keyboard = []
    for company_name in company_names:
        keyboard.append([InlineKeyboardButton(company_name, callback_data=company_name)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('검색 결과:', reply_markup=reply_markup)

    # 사용자 상태 변경
    return SELECT_COMPANY

def select_company(update: Update, context: CallbackContext) -> int:
    global company_dict
    query = update.callback_query
    selected_company = query.data

    # 선택한 기업의 값 가져오기
    company_value = company_dict[selected_company]

    # 선택한 기업과 값 출력
    info = set_data(company_value)
    query.message.reply_text(f'{selected_company}\n{company_value}\n{info}')
    # 사용자 상태 초기화
    return ConversationHandler.END

def main():
    get_access_token()
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

   
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(CallbackQueryHandler(select_company))
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()