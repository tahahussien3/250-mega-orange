from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/activate", methods=["POST"])
def activate():
    data = request.json

    number = data.get("number")
    password = data.get("password")

    # ===== نفس كودك بالحرف =====

    url = "https://services.orange.eg/SignIn.svc/SignInUser"
    payload = {
        "appVersion": "9.0.1",
        "channel": {
            "ChannelName": "MobinilAndMe",
            "Password": "ig3yh*mk5l42@oj7QAR8yF"
        },
        "dialNumber": number,
        "isAndroid": True,
        "lang": "ar",
        "password": password}
    headers = {
        'User-Agent': "okhttp/4.10.0",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'Content-Type': "application/json; charset=UTF-8"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    try:
        AccessToken = response.json()['SignInUserResult']['AccessToken']
    except:
        return jsonify({"status": "fail", "message": "Number or password error"})

    url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
    payload = {
        "ChannelName": "MobinilAndMe",
        "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
        "Dial": number,
        "Language": "ar",
        "Module": "0",
        "Password": password}
    headers = {
        'User-Agent': "okhttp/4.10.0",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'AppVersion': "9.0.1",
        'OsVersion': "13",
        'IsAndroid': "true",
        'IsEasyLogin': "false",
        'Token': AccessToken,
        'Content-Type': "application/json; charset=UTF-8"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    try:
        Token = response.json()["Token"]
    except:
        return jsonify({"status": "fail", "message": "الرقم او كلمة السر غلط"})

    url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
    payload = {
        "Dial": number,
        "Language": "ar",
        "Token": Token}
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; 21061119AG Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/139.0.7258.158 Mobile Safari/537.36",
        'Accept': "application/json, text/plain, */*",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'Content-Type': "application/json",
        'sec-ch-ua-platform': "\"Android\"",
        'sec-ch-ua': "\"Not;A=Brand\";v=\"99\", \"Android WebView\";v=\"139\", \"Chromium\";v=\"139\"",
        'sec-ch-ua-mobile': "?1",
        'Origin': "https://services.orange.eg",
        'X-Requested-With': "com.orange.mobinilandmf",
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Accept-Language': "ar,en-US;q=0.9,en;q=0.8",}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    data = response.json()

    if data['ErrorCode'] == 1:
        return jsonify({"status": "fail", "message": "انت دخلت علي الفوازير النهارده جرب بكره"})

    questions = data["Questions"]
    answers_list = []

    for q in questions:
        for a in q["Answers"]:
            if a["IsCorrect"] == True:
                answers_list.append({
                    "QuestionId": a["QuestionId"],
                    "AnswerId": a["Id"]
                })
                break

    url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
    payload = {
        "Dial": number,
        "Language": "ar",
        "Token": Token,
        "Answers": answers_list}
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.json()['ErrorDescription'] == "FawazeerSuccess":
        return jsonify({"status": "success", "message": "Done send 250 mg"})
    else:
        return jsonify({"status": "fail", "message": response.json()['ErrorDescription']})

# ================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
