from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
# تفعيل CORS للسماح للموقع بالاتصال بالسيرفر
CORS(app)

@app.route('/activate', methods=['POST'])
def activate():
    # استلام البيانات كـ JSON لضمان أعلى توافق مع Railway
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"})
        
    number = data.get("phone")
    password = data.get("password")

    if not number or not password:
        return jsonify({"status": "error", "message": "بيانات ناقصة!"})

    # --- كود أورنج الخاص بك (بدون أي تعديل في المنطق) ---
    url_signin = "https://services.orange.eg/SignIn.svc/SignInUser"
    payload_signin = {
        "appVersion": "9.0.1",
        "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
        "dialNumber": number,
        "isAndroid": True,
        "lang": "ar",
        "password": password
    }
    headers_main = {
        'User-Agent': "okhttp/4.10.0",
        'Connection': "Keep-Alive",
        'Content-Type': "application/json; charset=UTF-8"
    }
    
    try:
        response_signin = requests.post(url_signin, data=json.dumps(payload_signin), headers=headers_main)
        AccessToken = response_signin.json()['SignInUserResult']['AccessToken']
    except Exception:
        return jsonify({"status": "error", "message": "رقم الهاتف أو كلمة السر غير صحيحة"})

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
        **headers_main,
        'AppVersion': "9.0.1",
        'OsVersion': "13",
        'IsAndroid': "true",
        'IsEasyLogin': "false",
        'Token': AccessToken
    }
    
    try:
        response_gen = requests.post(url_gen, data=json.dumps(payload_gen), headers=headers_gen)
        Token = response_gen.json()["Token"]
        
        url_q = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        payload_q = {"Dial": number, "Language": "ar", "Token": Token}
        headers_web = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13; 21061119AG)",
            'Content-Type': "application/json",
            'X-Requested-With': "com.orange.mobinilandmf",
            'Origin': "https://services.orange.eg"
        }
        
        response_q = requests.post(url_q, data=json.dumps(payload_q), headers=headers_web)
        data_q = response_q.json()
        
        if data_q.get('ErrorCode') == 1:
            return jsonify({"status": "error", "message": "لقد شاركت اليوم، جرب غداً"})

        questions = data_q.get("Questions", [])
        answers_list = []
        for q in questions:
            for a in q["Answers"]:
                if a["IsCorrect"]:
                    answers_list.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                    break
                    
        url_submit = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        payload_submit = {"Dial": number, "Language": "ar", "Token": Token, "Answers": answers_list}
        
        response_final = requests.post(url_submit, data=json.dumps(payload_submit), headers=headers_web)
        final_res = response_final.json()
        
        if final_res.get('ErrorDescription') == "FawazeerSuccess":
            return jsonify({"status": "success", "message": "تم إرسال الـ 250 ميجا بنجاح! ✅"})
        else:
            return jsonify({"status": "error", "message": final_res.get('ErrorDescription', 'حدث خطأ غير متوقع')})
            
    except Exception as e:
        return jsonify({"status": "error", "message": "حدث خطأ في الاتصال بخوادم أورنج"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
