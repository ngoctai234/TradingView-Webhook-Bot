# ----------------------------------------------- #
# Plugin Name           : TradingView-Webhook-Bot #
# Author Name           : fabston                 #
# File Name             : main.py                 #
# ----------------------------------------------- #

from handler import send_alert
import config
import time
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_timestamp():
    timestamp = time.strftime("%Y-%m-%d %X")
    return timestamp


@app.route("/webhook", methods=["POST"])
def webhook():
    whitelisted_ips = config.whitelisted_ips
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if client_ip not in whitelisted_ips:
        print(
            "[X]",
            get_timestamp(),
            f"Alert Received & Refused! (Unauthorized IP: {client_ip})",
        )
        return jsonify({"message": "Unauthorized"}), 401
    try:
        if request.method == "POST":
            key = request.args.get("key")
            if key == config.sec_key:
                msg = request.get_data(as_text=True).strip()
                telegram = request.args.get("telegram")
                discord = request.args.get("discord")
                slack = request.args.get("slack")
                data = {"msg": msg}
                if telegram:
                    data["telegram"] = telegram
                if discord:
                    data["discord"] = discord
                if slack:
                    data["slack"] = slack
                print(get_timestamp(), "Alert Received & Sent!")
                send_alert(data)
                return jsonify({"message": "Webhook received successfully"}), 200

            else:
                print("[X]", get_timestamp(), "Alert Received & Refused! (Wrong Key)")
                return jsonify({"message": "Unauthorized"}), 401

    except Exception as e:
        print("[X]", get_timestamp(), "Error:\n>", e)
        return jsonify({"message": "Error"}), 400


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8090)
