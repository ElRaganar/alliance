from flask import Flask, render_template, request, jsonify
import requests
import threading

app = Flask(__name__)

ALLIANCE_MAP = {
    "RIP": 36700257,
    "ZEN": 36700892,
    "AUN": 36700710,
    "BRO -558":36570597,
    "LOG -558":36570036,
    "UF -558":36570559,
    "1st -558":36570509,
    "HP-558":36569435,
    "GER -558":36569681,
    "RXR -558":36570402,
    "V-558":36570418


}

access_token_cache = {
    "token": None,
    "lock": threading.Lock()
}

def request_new_access_token():
    auth_url = 'https://eur-janus.gameloft.com/authorize'
    form_data = {
        'client_id': 'gah:1867:69703:9.0.0c:steam:steam',
        'username': 'anonymous:d2luMzJfc3RlYW1fNzY1NjExOTg4MzA3ODk3MzFfMTc0NjE5NDE4Nl+m3bRSBks4EoTGkY53wg1L',
        'password': 'Y1Yh5y0KyWgXTZCh',
        'scope': 'auth chat config leaderboard_ro lobby message social storage translation',
        'device_id': '389714701901586724',
        'for_credential_type': 'anonymous'
    }

    response = requests.post(auth_url, data=form_data)
    response.raise_for_status()
    return response.json()['access_token']

def get_cached_access_token():
    with access_token_cache["lock"]:
        if access_token_cache["token"] is None:
            access_token_cache["token"] = request_new_access_token()
        return access_token_cache["token"]

@app.route('/')
def index():
    return render_template('index.html', alliances=list(ALLIANCE_MAP.keys()))

@app.route('/get_chat_url')
def get_chat_url():
    alliance_name = request.args.get('alliance')
    if alliance_name not in ALLIANCE_MAP:
        return jsonify({"error": "Invalid alliance"}), 400

    alliance_id = ALLIANCE_MAP[alliance_name]
    access_token = get_cached_access_token()

    arion_url = f"https://eur-arion.gameloft.com/chat/rooms/gah.room.alliance.{alliance_id}/subscribe"
    headers = {
        "Accept": "application/json"
    }
    params = {
        "access_token": access_token,
        "language": "en"
    }

    try:
        resp = requests.get(arion_url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Expecting keys: 'cmd', 'listen', 'httpslistenurl'
        return jsonify({
            "cmd": data.get("cmd_url"),
            "listen": data.get("listen_url"),
            "httpslistenurl": data.get("https_listen_url")
        })
    except Exception as e:
        return jsonify({"error":"Unable to connect" }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)