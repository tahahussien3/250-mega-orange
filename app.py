from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

@app.route('/activate', methods=['POST'])
def activate():
    number = request.form.get("phone")
    password = request.form.get("password")

    if not number or not password:
        return jsonify({"status": "error", "message": "Missing Data"})

    # --- بداية كود أورنج ---
    url = "https://services.orange.eg/SignIn.svc/SignInUser"
    payload = {
        "appVersion": "9.0.1",
        "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
        "dialNumber": number,
        "isAndroid": True,
        "lang": "ar",
        "password": password
    }
    headers = {
        'User-Agent': "okhttp/4.10.0",
        'Connection': "Keep-Alive",
        'Content-Type': "application/json; charset=UTF-8"
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    try:
        AccessToken = response.json()['SignInUserResult']['AccessToken']
    except:
        return jsonify({"status": "error", "message": "Number or password error"})

    url_gen = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
    payload_gen = {
        "ChannelName": "MobinilAndMe",
        "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
        "Dial": number,
        "Language": "ar",
        "Module": "0",
        "Password": password
    }
    
    response_gen = requests.post(url_gen, data=json.dumps(payload_gen), headers=headers)
    Token = response_gen.json()["Token"]
    
    url_q = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
    # السطر اللي كان فيه المشكلة (تم ضبط المحاذاة هنا)
    payload_q = {
        "Dial": number,
        "Language": "ar",
        "Token": Token
    }
    
    headers_q = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; 21061119AG Build/TP1A.220624.014)",
        'Content-Type': "application/json",
        'X-Requested-With': "com.orange.mobinilandmf"
    }
    
    response_q = requests.post(url_q, data=json.dumps(payload_q), headers=headers_q)
    data = response_q.json()
    
    if data.get('ErrorCode') == 1:
        return jsonify({"status": "error", "message": "جرب بكرة"})

    questions = data.get("Questions", [])
    answers_list = []
    for q in questions:
        for a in q["Answers"]:
            if a["IsCorrect"]:
                answers_list.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                break
                
    url_submit = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
    payload_submit = {
        "Dial": number,
        "Language": "ar",
        "Token": Token,
        "Answers": answers_list
    }
    
    response_final = requests.post(url_submit, data=json.dumps(payload_submit), headers=headers_q)
    
    if response_final.json().get('ErrorDescription') == "FawazeerSuccess":
        return jsonify({"status": "success", "message": "Done send 250 mg"})
    else:
        return jsonify({"status": "error", "message": "Try again later"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
