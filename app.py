from flask import Flask, request, jsonify
import requests
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def orange_logic(number, password):
    # شرط أن يبدأ الرقم بـ 012
    if not str(number).startswith("012"):
        return {"status": "error", "message": "عذراً، العرض مخصص لأرقام أورانج فقط (012)"}

    session = requests.Session()
    
    # --- الخطوة 1: تسجيل الدخول ---
    url_signin = "https://services.orange.eg/SignIn.svc/SignInUser"
    payload_signin = {
        "appVersion": "9.0.1",
        "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
        "dialNumber": number,
        "isAndroid": True,
        "lang": "ar",
        "password": password
    }
    headers_signin = {
        'User-Agent': "okhttp/4.10.0",
        'Content-Type': "application/json; charset=UTF-8"
    }

    try:
        res1 = session.post(url_signin, data=json.dumps(payload_signin), headers=headers_signin, timeout=20)
        auth_data = res1.json()
        
        if 'SignInUserResult' not in auth_data or 'AccessToken' not in auth_data['SignInUserResult']:
            return {"status": "error", "message": "رقم الهاتف أو كلمة السر خطأ"}
        
        access_token = auth_data['SignInUserResult']['AccessToken']

        # --- الخطوة 2: Generate Token ---
        url_gen = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        payload_gen = {
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number,
            "Language": "ar",
            "Module": "0",
            "Password": password
        }
        headers_gen = {
            'User-Agent': "okhttp/4.10.0",
            'Token': access_token,
            'Content-Type': "application/json; charset=UTF-8"
        }
        res2 = session.post(url_gen, data=json.dumps(payload_gen), headers=headers_gen, timeout=20)
        token_final = res2.json().get("Token")

        # --- الخطوة 3: جلب الأسئلة (نفس منطق الاسكربت) ---
        url_q = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        payload_q = {"Dial": number, "Language": "ar", "Token": token_final}
        headers_q = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13; 21061119AG Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/139.0.7258.158 Mobile Safari/537.36",
            'Content-Type': "application/json",
            'X-Requested-With': "com.orange.mobinilandmf"
        }
        res3 = session.post(url_q, data=json.dumps(payload_q), headers=headers_q, timeout=20)
        data = res3.json()

        # التحقق من ErrorCode 1 (نفس رسالة الاسكربت)
        if data.get('ErrorCode') == 1:
            return {"status": "error", "message": "انت دخلت علي الفوازير النهارده جرب بكره"}

        # حل الأسئلة
        questions = data.get("Questions", [])
        answers_list = []
        for q in questions:
            for a in q["Answers"]:
                if a["IsCorrect"]:
                    answers_list.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                    break

        # --- الخطوة 4: Submit ---
        url_sub = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        payload_sub = {"Dial": number, "Language": "ar", "Token": token_final, "Answers": answers_list}
        res4 = session.post(url_sub, data=json.dumps(payload_sub), headers=headers_q, timeout=20)
        
        if res4.json().get('ErrorDescription') == "FawazeerSuccess":
            return {"status": "success", "message": "Done send 250 mg"}
        else:
            return {"status": "error", "message": res4.json().get('ErrorDescription')}

    except Exception as e:
        return {"status": "error", "message": "حدث خطأ في الاتصال، حاول لاحقاً"}

@app.route('/activate', methods=['POST'])
def activate():
    num = request.form.get('phone')
    pwd = request.form.get('password')
    return jsonify(orange_logic(num, pwd))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
