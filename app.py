from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app) # Allows your HTML to talk to this script

@app.route('/get-offer', methods=['POST'])
def get_offer():
    data = request.json
    number = data.get("phone")
    password = data.get("password")

    # --- START OF YOUR UNCHANGED LOGIC ---
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
        'Content-Type': "application/json; charset=UTF-8"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        AccessToken = response.json()['SignInUserResult']['AccessToken']
    except:
        return jsonify({"status": "error", "message": "رقم الهاتف أو كلمة المرور غير صحيحة"}), 400

    # Token Generation
    url_token = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
    payload_token = {
        "ChannelName": "MobinilAndMe",
        "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
        "Dial": number,
        "Language": "ar",
        "Module": "0",
        "Password": password
    }
    res_token = requests.post(url_token, data=json.dumps(payload_token), headers=headers)
    Token = res_token.json()["Token"]

    # Questions Logic
    url_ques = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
    payload_ques = {"Dial": number, "Language": "ar", "Token": Token}
    res_ques = requests.post(url_ques, data=json.dumps(payload_ques), headers=headers)
    data_ques = res_ques.json()

    if data_ques['ErrorCode'] == 1:
        return jsonify({"status": "info", "message": "لقد استنفدت محاولات اليوم، جرب غداً"})

    questions = data_ques["Questions"]
    answers_list = []
    for q in questions:
        for a in q["Answers"]:
            if a["IsCorrect"]:
                answers_list.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                break

    # Submit Logic
    url_submit = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
    payload_submit = {"Dial": number, "Language": "ar", "Token": Token, "Answers": answers_list}
    res_final = requests.post(url_submit, data=json.dumps(payload_submit), headers=headers)
    
    if res_final.json().get('ErrorDescription') == "FawazeerSuccess":
        return jsonify({"status": "success", "message": "تم إرسال 250 ميجا بنجاح!"})
    else:
        return jsonify({"status": "error", "message": res_final.json().get('ErrorDescription')})
    # --- END OF YOUR UNCHANGED LOGIC ---

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    app.run(host='0.0.0.0', port=port)
