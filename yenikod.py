import os
import time
import requests

API_URL = "https://api.ayechat.ai/token"

# Sabit cURL başlıkları
HEADERS = {
    "sec-ch-ua-platform": '"Windows"',
    "Authorization": "Bearer eyJraWQiOiJzdHdSdDYyTzBUdWFtc0gyQjZFWDhqQzdONXRWbVFlWjNkcnNza2tZb3IwPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI2NGM4NjQ4OC1lMDgxLTcwYTAtM2U4Mi04YjdiOTEzOWQwMmYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbS91cy1lYXN0LTFfYmxOOE0xdWYwIiwiY29nbml0bzp1c2VybmFtZSI6IjY0Yzg2NDg4LWUwODEtNzBhMC0zZTgyLThiN2I5MTM5ZDAyZiIsIm9yaWdpbl9qdGkiOiI4OGMxNDFlMi0xYzQzLTRiZmQtOTk4ZS01MjU4NTY5MDdhMzIiLCJhdWQiOiIxZzFmMzlhdTBhb2toMGo5YjRwYWU2ZjlzYiIsImV2ZW50X2lkIjoiYTljMGUyNDItMGQ5ZS00NGMwLTlhNmQtMmUzOTUwMjA4NTNjIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3ODc0NzcxOTMsImV4cCI6MTc4NzU4OTI3NywiaWF0IjoxNzg3NTg1Njc3LCJqdGkiOiJmMWRjODhjNi00ZWYyLTQ2MzMtOGFlMS1kOTIzZmI1YzYxNDMiLCJlbWFpbCI6InV5Z3Vuc3V1QGdtYWlsLmNvbSJ9.B9QXmudL2KSPv0b9xtpTOyJ-KDMkNpUlo5d05EChdeG-XvwWsY0TGrTWDAAVdnKw8hRzPj3674m1JYIW8pDn7K0xN2kuK0CA-g3JWwqToYVJQtWxpOGg62NIjTMadgcWx3UGPlpfWjBLpcFvRW00IgOp5sOted6qLRSqZtnUkXiIPvtn5c4OxqaV650nn1DTqtAEwer9Ziw3pJGxp609cfWR3l9EjrymO-KLysON8P_NxGKFnaiaqbwrJQ0y6zZd0PMrH3ckEOp8n7BiH_gXi26V5S2lE7A1cuLhkW_OqfPMQtAST1_n6adtKmQ83ESRFrFZeBXUBRjmBZP4HETiIQ",
    "Referer": "https://ayechat.ai/",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
}

def get_ayechat_token(email: str):
    payload = {"user_id": email}
    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, str):
                return data
            if isinstance(data, dict):
                return data.get("token") or data.get("access_token") or str(data)
        else:
            print(f"Hata ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"İstek hatası: {e}")
    return None

def save_token(email: str, token: str):
    with open("ensonki.txt", "a", encoding="utf-8") as f:
        f.write(f"{token}\n")
    with open("tokenlar.txt", "a", encoding="utf-8") as f:
        f.write(f"{email} | {token}\n")

def main():
    if not os.path.exists("piro.txt"):
        print("piro.txt bulunamadı.")
        return

    with open("piro.txt", "r", encoding="utf-8") as f:
        emails = [line.strip() for line in f if line.strip()]

    if not emails:
        print("piro.txt dosyası boş.")
        return

    print(f"Toplam {len(emails)} e-posta için cURL API isteği atılıyor...")
    print("=" * 50)

    success = 0
    for i, email in enumerate(emails):
        print(f"[{i+1}/{len(emails)}] İstek atılıyor: {email}")
        
        token = get_ayechat_token(email)
        if token:
            save_token(email, token)
            success += 1
            print(f"  -> Başarılı: {token[:25]}...")
        else:
            print(f"  -> Token alınamadı.")

        time.sleep(0.3)

    print("\nİşlem bitti!")
    print(f"Toplam Alınan: {success}/{len(emails)}")
    print("Kayıtlar: ensonki.txt ve tokenlar.txt")

if __name__ == "__main__":
    main()