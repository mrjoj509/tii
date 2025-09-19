from flask import Flask, request, jsonify
import requests
import re
from datetime import datetime

app = Flask(__name__)

def timestamp_to_readable(ts):
    try:
        return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

@app.route("/tiktok-user", methods=["GET"])
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

        # ====== Extract user info ======
        user = {}
        user["id"] = re.search(r'"id":"(\d+)"', html).group(1) if re.search(r'"id":"(\d+)"', html) else None
        user["uniqueId"] = re.search(r'"uniqueId":"(.*?)"', html).group(1) if re.search(r'"uniqueId":"(.*?)"', html) else username
        user["nickname"] = re.search(r'"nickname":"(.*?)"', html).group(1) if re.search(r'"nickname":"(.*?)"', html) else None
        user["signature"] = re.search(r'"signature":"(.*?)"', html).group(1) if re.search(r'"signature":"(.*?)"', html) else None
        user["secUid"] = re.search(r'"secUid":"(.*?)"', html).group(1) if re.search(r'"secUid":"(.*?)"', html) else None
        user["avatar"] = {
            "larger": re.search(r'"avatarLarger":"(.*?)"', html).group(1) if re.search(r'"avatarLarger":"(.*?)"', html) else None,
            "medium": re.search(r'"avatarMedium":"(.*?)"', html).group(1) if re.search(r'"avatarMedium":"(.*?)"', html) else None,
            "thumb": re.search(r'"avatarThumb":"(.*?)"', html).group(1) if re.search(r'"avatarThumb":"(.*?)"', html) else None
        }
        create_time = re.search(r'"createTime":(\d+)', html)
        user["createTime"] = int(create_time.group(1)) if create_time else None
        user["createTimeReadable"] = timestamp_to_readable(user["createTime"])
        nick_mod = re.search(r'"nickNameModifyTime":(\d+)', html)
        user["nickNameModifyTime"] = int(nick_mod.group(1)) if nick_mod else None
        user["nickNameModifyTimeReadable"] = timestamp_to_readable(user["nickNameModifyTime"])
        verified = re.search(r'"verified":(true|false)', html)
        user["verified"] = True if verified and verified.group(1)=="true" else False
        region = re.search(r'"region":"(.*?)"', html)
        user["region"] = region.group(1) if region else None
        user["country"] = user["region"]
        language = re.search(r'"language":"(.*?)"', html)
        user["language"] = language.group(1) if language else None
        risk = re.search(r'"risk":(.*?)[,}]', html)
        user["risk"] = risk.group(1) if risk else None
        device_id = re.search(r'"device_id":(\d+)', html)
        user["device_id"] = int(device_id.group(1)) if device_id else None
        ip = re.search(r'"ip":"(.*?)"', html)
        user["ip"] = ip.group(1) if ip else None

        # ====== Extract stats ======
        stats = {}
        stats["followerCount"] = int(re.search(r'"followerCount":(\d+)', html).group(1)) if re.search(r'"followerCount":(\d+)', html) else 0
        stats["followingCount"] = int(re.search(r'"followingCount":(\d+)', html).group(1)) if re.search(r'"followingCount":(\d+)', html) else 0
        stats["heart"] = int(re.search(r'"heartCount":(\d+)', html).group(1)) if re.search(r'"heartCount":(\d+)', html) else 0
        stats["heartCount"] = stats["heart"]
        stats["videoCount"] = int(re.search(r'"videoCount":(\d+)', html).group(1)) if re.search(r'"videoCount":(\d+)', html) else 0
        stats["diggCount"] = int(re.search(r'"diggCount":(\d+)', html).group(1)) if re.search(r'"diggCount":(\d+)', html) else 0
        stats["friendCount"] = int(re.search(r'"friendCount":(\d+)', html).group(1)) if re.search(r'"friendCount":(\d+)', html) else 0

        statsV2 = {k:str(v) for k,v in stats.items()}

        # ====== Build final JSON ======
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
