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
from typing import Tuple, Optional
from flask import Flask, request, jsonify
from urllib.parse import unquote

try:
    import SignerPy
except ImportError:
    os.system("pip install --upgrade pip")
    os.system("pip install SignerPy")
    import SignerPy


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
            "rc-verification-sg.tiktokv.com",
        ]

        self.params = {
            "device_platform": "android",
            "ssmix": "a",
            "channel": "googleplay",
            "aid": "1233",
            "app_name": "musical_ly",
            "version_code": "360505",
            "version_name": "36.5.5",
            "manifest_version_code": "2023605050",
            "update_version_code": "2023605050",
            "ab_version": "36.5.5",
            "os_version": "10",
            "device_id": 0,
            "app_version": "30.1.2",
            "request_from": "profile_card_v2",
            "request_from_scene": "1",
            "scene": "1",
            "mix_mode": "1",
            "os_api": "34",
            "ac": "wifi",
            "request_tag_from": "h5",
        }

        self.headers = {
            "User-Agent": f"com.zhiliaoapp.musically/2022703020 (Linux; U; Android 7.1.2; en; SM-N975F; Build/N2G48H;tt-ok/{str(random.randint(1, 10**19))})"
        }


# ============================================
# MobileFlowFlexible (email mode)
# ============================================
class MobileFlowFlexible:
    def __init__(self, account_param: str):
        self.input = account_param.strip()
        self.session = requests.Session()
        self.net = Network()

        if self.net.proxy:
            self.session.proxies = {
                "http": self.net.proxy,
                "https": self.net.proxy,
            }

        self.base_params = self.net.params.copy()
        try:
            self.base_params = SignerPy.get(params=self.base_params)
        except Exception as e:
            print("Warning: SignerPy.get failed:", e)

        self.base_params.update(
            {
                "device_type": f"rk{random.randint(3000, 4000)}s_{uuid.uuid4().hex[:4]}",
                "language": "AR",
            }
        )
        self.headers = self.net.headers.copy()

    async def find_passport_ticket(self, timeout_per_host: int = 10):
        acct = self.input
        for host in self.net.hosts:
            params = self.base_params.copy()
            ts = int(time.time())
            params["ts"] = ts
            params["_rticket"] = int(ts * 1000)
            params["account_param"] = acct
            try:
                signature = SignerPy.sign(params=params)
            except Exception as e:
                print(f"[LOG] SignerPy.sign failed for host {host}: {e}")
                continue

            headers = self.headers.copy()
            headers.update(signature)

            url = f"https://{host}/passport/account_lookup/email/"
            try:
                resp = await asyncio.to_thread(
                    self.session.post,
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout_per_host,
                )
                j = resp.json()
                if resp.status_code != 200:
                    continue
                accounts = j.get("data", {}).get("accounts", [])
                if not accounts:
                    continue
                first = accounts[0]
                ticket = (
                    first.get("passport_ticket")
                    or first.get("not_login_ticket")
                    or None
                )
                username = first.get("user_name") or first.get("username") or None
                if ticket:
                    return ticket, acct, j
                if username and not ticket:
                    return None, acct, j
            except Exception as e:
                print(f"[{host}] error: {e}")
                continue
        return None, None, None

    async def send_code_using_ticket(
        self, passport_ticket: str, timeout_mailbox: int = 120
    ):
        params = self.base_params.copy()
        ts = int(time.time())
        params["ts"] = ts
        params["_rticket"] = int(ts * 1000)
        params["not_login_ticket"] = passport_ticket
        params["email"] = self.input
        params["type"] = "3737"
        params.pop("fixed_mix_mode", None)
        params.pop("account_param", None)

        try:
            signature = SignerPy.sign(params=params)
        except Exception as e:
            print("[LOG] SignerPy.sign failed for send_code:", e)
            return None, None

        headers = self.headers.copy()
        headers.update(signature)

        for host in self.net.send_hosts:
            url = f"https://{host}/passport/email/send_code"
            try:
                resp = await asyncio.to_thread(
                    self.session.post, url, params=params, headers=headers, timeout=10
                )
                j = resp.json()
                print(
                    f"[send_code {host}] response: {json.dumps(j, ensure_ascii=False)[:2000]}"
                )

                dest = None
                for k in [
                    "send_to",
                    "destination",
                    "target",
                    "email",
                    "mask",
                    "email_mask",
                    "phone_mask",
                ]:
                    if k in j:
                        dest = j[k]
                        break
                if not dest:
                    if "data" in j:
                        for k in [
                            "send_to",
                            "destination",
                            "email",
                            "email_mask",
                            "phone_mask",
                        ]:
                            if k in j["data"]:
                                dest = j["data"][k]
                                break

                result = {
                    "status": j.get("message") or j.get("status"),
                    "host": host,
                    "destination": dest,
                    "raw": j,
                }
                return result, self.input
            except Exception as e:
                print(f"[LOG] send_code error {host}: {e}")
                continue
        return None, self.input


# ============================================
# Flask API
# ============================================
app = Flask(__name__)


@app.route("/extract", methods=["GET"])
def extract():
    raw_email = request.args.get("email", "")
    timeout_mailbox = int(request.args.get("timeout_mailbox", "120"))
    email = unquote(raw_email).strip()

    print(f"[LOG] استعلام جديد بالايميل: {email}")

    flow = MobileFlowFlexible(account_param=email)

    async def run_flow():
        ticket, used_variant, resp_json = await flow.find_passport_ticket()
        if not ticket:
            return {
                "input": email,
                "status": "not_found",
                "username": None,
                "passport_ticket": None,
                "used_variant": used_variant,
                "raw_response_snippet": None
                if resp_json is None
                else str(resp_json)[:500],
                "tiktokinfo": None,
            }

        print(f"[LOG] نجح استخراج التذكرة: {ticket}")
        send_result, mail_used = await flow.send_code_using_ticket(
            passport_ticket=ticket, timeout_mailbox=timeout_mailbox
        )

        return {
            "input": email,
            "status": "success" if send_result else "error",
            "passport_ticket": ticket,
            "mail_used": mail_used,
            "send_result": send_result,
        }

    result = asyncio.run(run_flow())
    return jsonify(result)


# ============================================
# Run Flask
# ============================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
