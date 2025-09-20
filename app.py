from flask import Flask, request, jsonify
import requests
import re
from datetime import datetime

app = Flask(__name__)

def ts_to_date(ts):
    try:
        return datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

def extract(pattern, text, group=1, cast=None):
    match = re.search(pattern, text)
    if not match:
        return None
    value = match.group(group)
    if cast:
        try:
            return cast(value)
        except:
            return None
    return value

@app.route("/tiktok-user1", methods=["GET"])
def tiktok_user():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "missing username"}), 400

    url = f"https://www.tiktok.com/@{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return jsonify({"error": "User not found"}), 404

        html = resp.text

        # ===== User Data =====
        createTime = extract(r'"createTime":(\d+)', html, cast=int)
        nickNameModifyTime = extract(r'"nickNameModifyTime":(\d+)', html, cast=int)

        user = {
            "id": extract(r'"id":"(\d+)"', html),
            "uniqueId": extract(r'"uniqueId":"(.*?)"', html) or username,
            "nickname": extract(r'"nickname":"(.*?)"', html),
            "secUid": extract(r'"secUid":"(.*?)"', html),
            "signature": extract(r'"signature":"(.*?)"', html),
            "avatar": {
                "larger": extract(r'"avatarLarger":"(.*?)"', html),
                "medium": extract(r'"avatarMedium":"(.*?)"', html),
                "thumb": extract(r'"avatarThumb":"(.*?)"', html)
            },
            "createTime": createTime,
            "createTimeReadable": ts_to_date(createTime),
            "nickNameModifyTime": nickNameModifyTime,
            "nickNameModifyTimeReadable": ts_to_date(nickNameModifyTime),
            "verified": True if extract(r'"verified":(true|false)', html) == "true" else False,
            "region": extract(r'"region":"(.*?)"', html),
            "country": extract(r'"region":"(.*?)"', html),  # مؤقت نستخدم نفس القيمة
            "language": extract(r'"language":"(.*?)"', html),
            "privateAccount": True if extract(r'"privateAccount":(true|false)', html) == "true" else False,
            "isOrganization": extract(r'"isOrganization":(\d+)', html, cast=int),
            "roomId": extract(r'"roomId":"(.*?)"', html),
            "openFavorite": True if extract(r'"openFavorite":(true|false)', html) == "true" else False,
            "commentSetting": extract(r'"commentSetting":(\d+)', html, cast=int),
            "duetSetting": extract(r'"duetSetting":(\d+)', html, cast=int),
            "stitchSetting": extract(r'"stitchSetting":(\d+)', html, cast=int),
            "downloadSetting": extract(r'"downloadSetting":(\d+)', html, cast=int),
            "profileTab": {
                "showMusicTab": True if extract(r'"showMusicTab":(true|false)', html) == "true" else False,
                "showQuestionTab": True if extract(r'"showQuestionTab":(true|false)', html) == "true" else False,
                "showPlayListTab": True if extract(r'"showPlayListTab":(true|false)', html) == "true" else False,
            },
            "commerceUserInfo": {
                "commerceUser": True if extract(r'"commerceUser":(true|false)', html) == "true" else False
            },
            "ttSeller": True if extract(r'"ttSeller":(true|false)', html) == "true" else False,
            "canExpPlaylist": True if extract(r'"canExpPlaylist":(true|false)', html) == "true" else False,
            "profileEmbedPermission": extract(r'"profileEmbedPermission":(\d+)', html, cast=int),
            "isEmbedBanned": True if extract(r'"isEmbedBanned":(true|false)', html) == "true" else False,
            "secret": True if extract(r'"secret":(true|false)', html) == "true" else False,
            "isADVirtual": True if extract(r'"isADVirtual":(true|false)', html) == "true" else False,
            "relation": extract(r'"relation":(\d+)', html, cast=int),
            "risk": extract(r'"risk":(.*?)[,}]', html),
            "device_id": extract(r'"device_id":(\d+)', html, cast=int),
            "ip": extract(r'"ip":"(.*?)"', html)
        }

        # ===== Stats =====
        stats = {
            "followerCount": extract(r'"followerCount":(\d+)', html, cast=int) or 0,
            "followingCount": extract(r'"followingCount":(\d+)', html, cast=int) or 0,
            "heart": extract(r'"heartCount":(\d+)', html, cast=int) or 0,
            "videoCount": extract(r'"videoCount":(\d+)', html, cast=int) or 0,
            "friendCount": extract(r'"friendCount":(\d+)', html, cast=int) or 0,
            "diggCount": extract(r'"diggCount":(\d+)', html, cast=int) or 0
        }

        statsV2 = {k: str(v) for k, v in stats.items()}

        response = {
            "user": user,
            "stats": stats,
            "statsV2": statsV2,
            "itemList": []
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
