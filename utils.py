import pandas as pd
import os
from datetime import datetime

import requests

FAQ_FILE = 'faq.csv'
USAGE_LOG_FILE = 'usage_log.csv'
BOT_RULES_FILE = 'bot_rules.txt'
FLIGHT_API_BASE_URL = "http://extapi.jinair.com"
OPERATION_CONFIRMATION_API_URL = "https://ccsstg.jinair.com/event/sendOperationConfirmation"

def load_faq_data():
    """Loeads FAQ data from CSV into a Pandas DataFrame."""
    if not os.path.exists(FAQ_FILE):
        return pd.DataFrame(columns=['category', 'question', 'answer'])
    try:
        return pd.read_csv(FAQ_FILE)
    except Exception as e:
        print(f"Error loading FAQ data: {e}")
        return pd.DataFrame(columns=['category', 'question', 'answer'])

def save_faq_data(df):
    """Saves the DataFrame to CSV."""
    df.to_csv(FAQ_FILE, index=False)

def get_faq_as_text():
    """Formats the FAQ data into a string for the LLM system instruction."""
    df = load_faq_data()
    if df.empty:
        return "FAQ 데이터가 없습니다."
    
    faq_text = ""
    for index, row in df.iterrows():
        faq_text += f"Q: {row['question']}\nA: {row['answer']}\n"
    return faq_text

def log_usage(model_name, prompt_tokens, candidate_tokens):
    """Logs API usage to a CSV file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_entry = pd.DataFrame([{
        'timestamp': timestamp,
        'model': model_name,
        'prompt_tokens': prompt_tokens,
        'candidate_tokens': candidate_tokens
    }])

    if not os.path.exists(USAGE_LOG_FILE):
        new_entry.to_csv(USAGE_LOG_FILE, index=False)
    else:
        new_entry.to_csv(USAGE_LOG_FILE, mode='a', header=False, index=False)

def load_usage_data():
    """Loads usage logs from CSV."""
    if not os.path.exists(USAGE_LOG_FILE):
        return pd.DataFrame(columns=['timestamp', 'model', 'prompt_tokens', 'candidate_tokens'])
    try:
        df = pd.read_csv(USAGE_LOG_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f"Error loading usage logs: {e}")
        return pd.DataFrame(columns=['timestamp', 'model', 'prompt_tokens', 'candidate_tokens'])

def load_bot_rules():
    """Loads custom bot rules from a text file."""
    if not os.path.exists(BOT_RULES_FILE):
        # Default rules if file doesn't exist
        return "친절하고 상냥하게 답변해주세요."
    try:
        with open(BOT_RULES_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading bot rules: {e}")
        return "규칙을 불러오는 중 오류가 발생했습니다."

def save_bot_rules(rules_text):
    """Saves custom bot rules to a text file."""
    try:
        with open(BOT_RULES_FILE, 'w', encoding='utf-8') as f:
            f.write(rules_text)
        return True
    except Exception as e:
        print(f"Error saving bot rules: {e}")
        return False

def check_api_status(url):
    """Checks if the API is reachable."""
    try:
        response = requests.get(url, timeout=5)
        return True, response.status_code, response.elapsed.total_seconds()
    except Exception as e:
        return False, str(e), 0

def send_operation_confirmation_api(flight_date: str, flight_number: str, email: str):
    """
    운항정보확인서 발송 API 호출 함수
    """
    url = OPERATION_CONFIRMATION_API_URL
    payload = {
        "flightDate": flight_date,
        "flightNumber": flight_number,
        "searchFlightId": "0", 
        "email": email,
        "requestBy": "진에어 고객서비스센터"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

PNR_DETAIL_API_URL = "https://ccs.jinair.com/event/getPnrDetail"

def get_pnr_detail_api(pnr: str):
    """
    예약 상세 조회 API 호출 함수
    """
    url = PNR_DETAIL_API_URL
    payload = {
        "searchNumber": pnr
    }
    
    # User-Agent 헤더 추가 (봇 차단 방지용)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


