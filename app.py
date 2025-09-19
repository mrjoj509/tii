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
        data = {}

        # Display name
        match = re.search(r'"nickname":"(.*?)"', html)
        data["display_name"] = match.group(1) if match else None

        # Username
        match = re.search(r'"uniqueId":"(.*?)"', html)
        data["username"] = match.group(1) if match else username

        # User ID
        match = re.search(r'"id":"(\d+)"', html)
        data["user_id"] = match.group(1) if match else None

        # Bio / Signature
        match = re.search(r'"signature":"(.*?)"', html)
        data["bio"] = match.group(1) if match else None

        # Followers
        match = re.search(r'"followerCount":(\d+)', html)
        data["followers"] = int(match.group(1)) if match else None

        # Following
        match = re.search(r'"followingCount":(\d+)', html)
        data["following"] = int(match.group(1)) if match else None

        # Likes / Hearts
        match = re.search(r'"heartCount":(\d+)', html)
        data["likes"] = int(match.group(1)) if match else None

        # Avatar
        match = re.search(r'"avatarLarger":"(.*?)"', html)
        data["avatar"] = match.group(1) if match else None

        # Region / Country
        match = re.search(r'"region":"(.*?)"', html)
        data["region"] = match.group(1) if match else None

        # Creation Time
        match = re.search(r'"createTime":(\d+)', html)
        if match:
            data["create_time"] = datetime.utcfromtimestamp(int(match.group(1))).strftime('%Y-%m-%d %H:%M:%S')
        else:
            data["create_time"] = None

        # Profile URL
        data["profile_url"] = f"https://www.tiktok.com/@{username}"

        # أي بيانات مهمة أخرى ممكن إضافتها
        important_matches = re.findall(r'"verified":(true|false)', html)
        data["verified"] = True if important_matches and important_matches[0]=="true" else False

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
