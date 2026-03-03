import os
import time
import json
import requests


BOT_TOKEN = "8655958696:AAF6_JR73nDAGahnNDhb_1LBw5YpmrYYcQA"  
CHAT_ID = "1396074427" 


SEARCH_TEXT = "AI-автоматизация OR специалист по нейросетям"
AREA = 1  # Ростов-на-Дону
FILE_NAME = "sent_vacancies.json"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, data=payload, timeout=10)
        r.raise_for_status()
        print("Сообщение отправлено")
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

def load_sent_ids():
    """Загружает список отправленных ID из JSON-файла"""
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_sent_ids(sent_ids):
    """Сохраняет список отправленных ID в JSON-файл"""
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(list(sent_ids), f, ensure_ascii=False, indent=2)

def fetch_vacancies():
    """Получает свежие вакансии с hh.ru"""
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": SEARCH_TEXT,
        "area": AREA,
        "per_page": 10,
        "order_by": "publication_time"
    }
    headers = {
        "User-Agent": "HH-Vacancy-Parser/1.0 (lola.artem7@mail.ru)"
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get("items", [])
    except Exception as e:
        print(f"Ошибка получения вакансий: {e}")
        return []

def format_vacancy(vac):
    """Форматирует вакансию в читаемое сообщение"""
    name = vac.get("name", "Без названия")
    employer = vac.get("employer", {}).get("name", "Не указан")
    salary = vac.get("salary")
    if salary:
        fr = salary.get("from")
        to = salary.get("to")
        curr = salary.get("currency", "RUR")
        if fr and to:
            salary_str = f"{fr} - {to} {curr}"
        elif fr:
            salary_str = f"от {fr} {curr}"
        elif to:
            salary_str = f"до {to} {curr}"
        else:
            salary_str = "Не указана"
    else:
        salary_str = "Не указана"
    url = vac.get("alternate_url", "")
    published = vac.get("published_at", "")[:10]
    
    msg = f"<b>🔔 Новая вакансия: {name}</b>\n"
    msg += f"🏢 Компания: {employer}\n"
    msg += f"💰 Зарплата: {salary_str}\n"
    msg += f"📅 Опубликовано: {published}\n"
    msg += f"🔗 <a href='{url}'>Ссылка</a>"
    return msg

def main():
    print(f"{time.ctime()}: Проверка вакансий...")
    sent_ids = load_sent_ids()
    vacancies = fetch_vacancies()
    if not vacancies:
        print("Нет вакансий или ошибка.")
        return
    
    new = []
    for vac in vacancies:
        vid = str(vac.get("id"))
        if vid not in sent_ids:
            new.append(vac)
            sent_ids.add(vid)
    
    print(f"Найдено новых: {len(new)}")
    for vac in new:
        msg = format_vacancy(vac)
        send_telegram_message(msg)
        time.sleep(1)  # задержка между отправками
    
    if new:
        save_sent_ids(sent_ids)

if __name__ == "__main__":
    main()