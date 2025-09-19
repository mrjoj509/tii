import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

def extract_regions(data):
    """دور على كل region في الريسبونس"""
    regions = []

    def find_regions(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "region":
                    regions.append(v)
                find_regions(v)
        elif isinstance(obj, list):
            for item in obj:
                find_regions(item)

    find_regions(data)

    return {
        "all_regions": regions,
        "unique_regions": list(set(regions)),
        "count": {r: regions.count(r) for r in set(regions)}
    }

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
        # نجيب بيانات الحساب
        url = f"https://www.tiktok.com/@{username}?lang=en"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        resp = requests.get(url, headers=headers)

        # استخراج JSON من الصفحة
        text = resp.text
        start = text.find('{"props":')
        end = text.rfind("}") + 1
        data = json.loads(text[start:end])

        # نحاول نوصل للـ userInfo
        user_info = data.get("webapp.user-detail", {}).get("userInfo", {})
        user = user_info.get("user", {})
        stats = user_info.get("stats", {})

        # نرتب الداتا
        result = {
            "id": user.get("id"),
            "uniqueId": user.get("uniqueId"),
            "nickname": user.get("nickname"),
            "signature": user.get("signature"),
            "avatar": user.get("avatarLarger"),
            "region": user.get("region"),
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
            },
            "regions_found": extract_regions(data)
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
