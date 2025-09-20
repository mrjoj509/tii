from flask import Flask, request, jsonify
import requests
import re
import json
from datetime import datetime

app = Flask(__name__)

def ts_to_date(ts):
    try:
        return datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@app.route("/tiktov1", methods=["GET"])
def tiktok_user():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "missing username"}), 400

    url = f"https://www.tiktok.com/@{username}?lang=en"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1 OPT/6.1.2"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return jsonify({"error": "User not found"}), 404

        html = resp.text

        # نبحث عن webapp.user-detail
        match = re.search(r'"webapp.user-detail":({.*?}),"webapp', html)
        if not match:
            return jsonify({"error": "Could not extract userInfo"}), 500

        data = json.loads(match.group(1))
        user = data.get("userInfo", {}).get("user", {})
        stats = data.get("userInfo", {}).get("stats", {})

        # ===== User Data =====
        createTime = user.get("createTime")
        nickNameModifyTime = user.get("nickNameModifyTime")

        user_parsed = {
            "id": user.get("id"),
            "uniqueId": user.get("uniqueId"),
            "nickname": user.get("nickname"),
            "secUid": user.get("secUid"),
            "signature": user.get("signature"),
            "avatar": {
                "larger": user.get("avatarLarger"),
                "medium": user.get("avatarMedium"),
                "thumb": user.get("avatarThumb")
            },
            "createTime": createTime,
            "createTimeReadable": ts_to_date(createTime),
            "nickNameModifyTime": nickNameModifyTime,
            "nickNameModifyTimeReadable": ts_to_date(nickNameModifyTime),
            "verified": user.get("verified", False),
            "region": user.get("region"),
            "country": user.get("region"),  # مؤقت نخليها نفس الريجون
            "language": user.get("language"),
            "privateAccount": user.get("privateAccount"),
            "isOrganization": user.get("isOrganization"),
            "roomId": user.get("roomId"),
            "openFavorite": user.get("openFavorite"),
            "commentSetting": user.get("commentSetting"),
            "duetSetting": user.get("duetSetting"),
            "stitchSetting": user.get("stitchSetting"),
            "downloadSetting": user.get("downloadSetting"),
            "profileTab": user.get("profileTab"),
            "commerceUserInfo": user.get("commerceUserInfo"),
            "ttSeller": user.get("ttSeller"),
            "canExpPlaylist": user.get("canExpPlaylist"),
            "profileEmbedPermission": user.get("profileEmbedPermission"),
            "isEmbedBanned": user.get("isEmbedBanned"),
            "secret": user.get("secret"),
            "isADVirtual": user.get("isADVirtual"),
            "relation": user.get("relation"),
            "risk": user.get("risk"),
            "device_id": user.get("device_id"),
            "ip": user.get("ip")
        }

        # ===== Stats =====
        statsV2 = {k: str(v) for k, v in stats.items()}

        response = {
            "user": user_parsed,
            "stats": stats,
            "statsV2": statsV2,
            "itemList": []
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
