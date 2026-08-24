import os
import re
import time
import random
import string
import requests

# ----------------------------- YAPILANDIRMA -----------------------------
CLIENT_ID = "1g1f39au0aokh0j9b4pae6f9sb"
REGION = "us-east-1"
COGNITO_URL = f"https://cognito-idp.{REGION}.amazonaws.com/"
EMAIL_API = "https://api.mail.tm"
FIXED_PASSWORD = "Ornek875554!"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://ayechat.ai/",
    "Origin": "https://ayechat.ai",
    "Content-Type": "application/x-amz-json-1.1",
    "x-amz-user-agent": "aws-amplify/6.15.9 auth/1 framework/1",
}

def cognito_request(target: str, body: dict):
    headers = DEFAULT_HEADERS.copy()
    headers["X-Amz-Target"] = f"AWSCognitoIdentityProviderService.{target}"
    resp = requests.post(COGNITO_URL, json=body, headers=headers, timeout=15)
    try:
        data = resp.json()
    except:
        data = {"message": resp.text}
        
    if resp.status_code != 200:
        error_type = data.get("__type", "UnknownError")
        message = data.get("message", resp.text)
        raise Exception(f"Cognito {target} [{error_type}]: {message}")
    return data

def generate_random_username(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_temp_email():
    try:
        domain_resp = requests.get(f"{EMAIL_API}/domains", timeout=10)
        if domain_resp.status_code != 200:
            return None, None
        domain = domain_resp.json()["hydra:member"][0]["domain"]
        username = generate_random_username()
        email = f"{username}@{domain}"

        account_resp = requests.post(
            f"{EMAIL_API}/accounts",
            json={"address": email, "password": FIXED_PASSWORD},
            timeout=10,
        )
        if account_resp.status_code == 201:
            token_resp = requests.post(
                f"{EMAIL_API}/token",
                json={"address": email, "password": FIXED_PASSWORD},
                timeout=10,
            )
            return email, token_resp.json().get("token")
    except Exception as e:
        print(f"E-posta oluşturma hatası: {e}")
    return None, None

def get_verification_code(email, token):
    print(f"Doğrulama kodu bekleniyor: {email}")
    start = time.time()
    while time.time() - start < 90:
        try:
            msg_resp = requests.get(
                f"{EMAIL_API}/messages",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            messages = msg_resp.json().get("hydra:member", [])
            for msg in messages:
                detail_resp = requests.get(
                    f"{EMAIL_API}/messages/{msg['id']}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10,
                )
                content = detail_resp.json().get("text", "") or detail_resp.json().get("html", "")
                if isinstance(content, list):
                    content = " ".join(content)
                code_match = re.search(r"\b\d{6}\b", str(content))
                if code_match:
                    return code_match.group(0)
            time.sleep(3)
        except Exception as e:
            print(f"Kod alma hatası: {e}")
            time.sleep(3)
    return None

def sign_up(email, password):
    body = {"Username": email, "Password": password, "ClientId": CLIENT_ID}
    try:
        cognito_request("SignUp", body)
        return True
    except Exception as e:
        print(f"Kayıt hatası: {e}")
        return False

def confirm_sign_up(email, code):
    body = {"Username": email, "ConfirmationCode": code, "ClientId": CLIENT_ID}
    try:
        cognito_request("ConfirmSignUp", body)
        return True
    except Exception as e:
        print(f"Aktivasyon hatası: {e}")
        return False

def save_account_instantly(email, password):
    try:
        with open("piro.txt", "a", encoding="utf-8") as f:
            f.write(f"{email}\n")
        with open("sonraki.txt", "a", encoding="utf-8") as f:
            f.write(f"{password}\n")
        return True
    except Exception as e:
        print(f"Dosya kayıt hatası: {e}")
        return False

def main():
    target_accounts = 100
    created = 0

    for f in ["piro.txt", "sonraki.txt", "ensonki.txt", "tokenlar.txt"]:
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as fh:
                fh.write("")

    print(f"Hesap oluşturma başladı. Hedef: {target_accounts}")
    print("=" * 50)

    while created < target_accounts:
        email, email_token = create_temp_email()
        if not email:
            print("E-posta oluşturulamadı, yeniden deneniyor...")
            time.sleep(2)
            continue

        print(f"Kayıt deneniyor: {email}")
        if not sign_up(email, FIXED_PASSWORD):
            time.sleep(1)
            continue
        print(f"Kayıt başarılı: {email}")

        code = get_verification_code(email, email_token)
        if not code:
            print(f"Doğrulama kodu zaman aşımına uğradı: {email}")
            time.sleep(1)
            continue
        print(f"Doğrulama kodu: {code}")

        if not confirm_sign_up(email, code):
            print(f"Hesap doğrulanamadı: {email}")
            time.sleep(1)
            continue
        print("Hesap doğrulandı!")

        if save_account_instantly(email, FIXED_PASSWORD):
            created += 1
            print(f"[{created}/{target_accounts}] Hesap piro.txt ve sonraki.txt dosyalarına kaydedildi.")
        
        time.sleep(1)

        if created % 20 == 0 and created > 0:
            print("20 hesap tamamlandı, 5 saniye bekleniyor...")
            time.sleep(5)

    print("\nTüm hesaplar başarıyla oluşturuldu ve kaydedildi!")

if __name__ == "__main__":
    main()