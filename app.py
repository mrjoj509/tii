from flask import Flask, request, Response
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

@app.route("/tiktok", methods=["GET"])
def tiktok_user():
    username = request.args.get("username")
    if not username:
        return Response(
            json.dumps({"error": "missing username"}, ensure_ascii=False, indent=4),
            mimetype="application/json",
            status=400
        )

    url = f"https://www.tiktok.com/@{username}?lang=en"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1 OPT/6.1.2"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return Response(
                json.dumps({"error": "User not found"}, ensure_ascii=False, indent=4),
                mimetype="application/json",
                status=404
            )

        html = resp.text
        match = re.search(r'"webapp.user-detail":({.*?}),"webapp', html)
        if not match:
            return Response(
                json.dumps({"error": "Could not extract userInfo"}, ensure_ascii=False, indent=4),
                mimetype="application/json",
                status=500
            )

        data = json.loads(match.group(1))
        user = data.get("userInfo", {}).get("user", {})
        stats = data.get("userInfo", {}).get("stats", {})

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
            "country": user.get("region"),
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

        statsV2 = {k: str(v) for k, v in stats.items()}

        response = {
            "user": user_parsed,
            "stats": stats,
            "statsV2": statsV2,
            "itemList": []
        }

        return Response(
            json.dumps(response, ensure_ascii=False, indent=4),
            mimetype="application/json"
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}, ensure_ascii=False, indent=4),
            mimetype="application/json",
            status=500
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
