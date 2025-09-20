import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import re

app = Flask(__name__)

def convert_time(epoch_time):
    try:
        return datetime.utcfromtimestamp(int(epoch_time)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

@app.route("/tiktok", methods=["GET"])
def get_tiktok_user():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "الرجاء إدخال اسم المستخدم ?username="}), 400

    try:
        url = f"https://www.tiktok.com/@{username}?lang=en"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1 OPT/6.1.2"
        }
        resp = requests.get(url, headers=headers)

        # نبحث عن window.__INIT_PROPS__ = {....};
        match = re.search(r"window\.__INIT_PROPS__\s*=\s*({.*?});</script>", resp.text, re.S)
        if not match:
            return jsonify({"error": "ما قدرت ألقط JSON من الصفحة"}), 500

        data = json.loads(match.group(1))

        user_info = data.get(f"/@{username}", {}).get("webapp.user-detail", {}).get("userInfo", {})
        user = user_info.get("user", {})
        stats = user_info.get("stats", {})

        result = {
            "id": user.get("id"),
            "uniqueId": user.get("uniqueId"),
            "nickname": user.get("nickname"),
            "signature": user.get("signature"),
            "avatar": user.get("avatarLarger"),
            "region": user.get("region"),  # ← فقط واحد
            "secUid": user.get("secUid"),
            "createTime": convert_time(user.get("createTime")),
            "nickNameModifyTime": convert_time(user.get("nickNameModifyTime")),
            "verified": user.get("verified"),
            "privateAccount": user.get("privateAccount"),
            "language": user.get("language"),
            "stats": {
                "followerCount": stats.get("followerCount"),
                "followingCount": stats.get("followingCount"),
                "heartCount": stats.get("heartCount"),
                "videoCount": stats.get("videoCount"),
            }
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
