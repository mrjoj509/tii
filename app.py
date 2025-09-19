from flask import Flask, request, jsonify
import requests
import re
from datetime import datetime

app = Flask(__name__)

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

        # ====== user info ======
        user = {}
        user["id"] = re.search(r'"id":"(\d+)"', html).group(1) if re.search(r'"id":"(\d+)"', html) else None
        user["uniqueId"] = re.search(r'"uniqueId":"(.*?)"', html).group(1) if re.search(r'"uniqueId":"(.*?)"', html) else username
        user["nickname"] = re.search(r'"nickname":"(.*?)"', html).group(1) if re.search(r'"nickname":"(.*?)"', html) else None
        user["signature"] = re.search(r'"signature":"(.*?)"', html).group(1) if re.search(r'"signature":"(.*?)"', html) else None
        user["avatarLarger"] = re.search(r'"avatarLarger":"(.*?)"', html).group(1) if re.search(r'"avatarLarger":"(.*?)"', html) else None
        user["avatarMedium"] = re.search(r'"avatarMedium":"(.*?)"', html).group(1) if re.search(r'"avatarMedium":"(.*?)"', html) else None
        user["avatarThumb"] = re.search(r'"avatarThumb":"(.*?)"', html).group(1) if re.search(r'"avatarThumb":"(.*?)"', html) else None
        user["createTime"] = int(re.search(r'"createTime":(\d+)', html).group(1)) if re.search(r'"createTime":(\d+)', html) else None
        verified_match = re.search(r'"verified":(true|false)', html)
        user["verified"] = True if verified_match and verified_match.group(1)=="true" else False
        user["region"] = re.search(r'"region":"(.*?)"', html).group(1) if re.search(r'"region":"(.*?)"', html) else None
        user["country"] = None  # لايوجد مصدر مباشر للدولة
        user["language"] = re.search(r'"language":"(.*?)"', html).group(1) if re.search(r'"language":"(.*?)"', html) else None
        user["secUid"] = re.search(r'"secUid":"(.*?)"', html).group(1) if re.search(r'"secUid":"(.*?)"', html) else None

        # ====== stats ======
        stats = {}
        stats["followerCount"] = int(re.search(r'"followerCount":(\d+)', html).group(1)) if re.search(r'"followerCount":(\d+)', html) else 0
        stats["followingCount"] = int(re.search(r'"followingCount":(\d+)', html).group(1)) if re.search(r'"followingCount":(\d+)', html) else 0
        stats["heart"] = int(re.search(r'"heartCount":(\d+)', html).group(1)) if re.search(r'"heartCount":(\d+)', html) else 0
        stats["heartCount"] = stats["heart"]
        stats["videoCount"] = int(re.search(r'"videoCount":(\d+)', html).group(1)) if re.search(r'"videoCount":(\d+)', html) else 0
        stats["diggCount"] = 0
        stats["friendCount"] = int(re.search(r'"friendCount":(\d+)', html).group(1)) if re.search(r'"friendCount":(\d+)', html) else 0

        # ====== statsV2 (كـ strings) ======
        statsV2 = {k:str(v) for k,v in stats.items()}

        # ====== response ======
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
