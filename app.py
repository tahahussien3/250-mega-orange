from flask import Flask, request, jsonify
import requests
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def orange_logic(number, password):
    session = requests.Session()
    
    # الخطوة 1: تسجيل الدخول (SignIn)
    signin_url = "https://services.orange.eg/SignIn.svc/SignInUser"
    signin_payload = {
        "appVersion": "9.0.1",
        "channel": {
            "ChannelName": "MobinilAndMe",
            "Password": "ig3yh*mk5l42@oj7QAR8yF"
        },
        "dialNumber": number,
        "isAndroid": True,
        "lang": "ar",
        "password": password
    }
    signin_headers = {
        'User-Agent': "okhttp/4.10.0",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json; charset=UTF-8"
    }

    try:
        res1 = session.post(signin_url, data=json.dumps(signin_payload), headers=signin_headers, timeout=20)
        auth_data = res1.json()
        
        if 'SignInUserResult' not in auth_data or 'AccessToken' not in auth_data['SignInUserResult']:
            return {"status": "error", "message": "رقم الهاتف أو كلمة السر خطأ", "raw": auth_data}
        
        access_token = auth_data['SignInUserResult']['AccessToken']

        # الخطوة 2: توليد التوكن (Generate Token)
        gen_url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        gen_payload = {
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number,
            "Language": "ar",
            "Module": "0",
            "Password": password
        }
        gen_headers = {
            'User-Agent': "okhttp/4.10.0",
            'Token': access_token,
            'Content-Type': "application/json; charset=UTF-8"
        }
        res2 = session.post(gen_url, data=json.dumps(gen_payload), headers=gen_headers, timeout=20)
        final_token = res2.json().get("Token")

        if not final_token:
            return {"status": "error", "message": "فشل في الحصول على توكن التفعيل", "raw": res2.json()}

        # الخطوة 3: جلب الأسئلة
        q_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        q_payload = {"Dial": number, "Language": "ar", "Token": final_token}
        q_headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.158 Mobile Safari/537.36",
            'Content-Type': "application/json",
            'X-Requested-With': "com.orange.mobinilandmf"
        }
        res3 = session.post(q_url, data=json.dumps(q_payload), headers=q_headers, timeout=20)
        q_data = res3.json()

        if q_data.get('ErrorCode') == 1:
            return {"status": "error", "message": "أنت دخلت علي الفوازير النهاردة، جرب بكرة", "raw": q_data}

        # الخطوة 4: حل الأسئلة
        questions = q_data.get("Questions", [])
        if not questions:
            return {"status": "error", "message": "لا توجد عروض متاحة حالياً", "raw": q_data}

        answers_list = []
        for q in questions:
            for a in q.get("Answers", []):
                if a.get("IsCorrect"):
                    answers_list.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                    break

        # الخطوة 5: الإرسال النهائي (Submit)
        sub_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        sub_payload = {
            "Dial": number,
            "Language": "ar",
            "Token": final_token,
            "Answers": answers_list
        }
        res4 = session.post(sub_url, data=json.dumps(sub_payload), headers=q_headers, timeout=20)
        result_data = res4.json()

        if result_data.get('ErrorDescription') == "FawazeerSuccess":
            return {"status": "success", "message": "مبروك! تم إرسال 250 ميجا هدية"}
        else:
            return {"status": "error", "message": result_data.get('ErrorDescription', 'فشلت العملية'), "raw": result_data}

    except Exception as e:
        return {"status": "error", "message": "حدث خطأ أثناء الاتصال بسيرفر أورانج", "debug": str(e)}

@app.route('/activate', methods=['POST'])
def activate():
    num = request.form.get('phone')
    pwd = request.form.get('password')
    if not num or not pwd:
        return jsonify({"status": "error", "message": "يرجى إدخال البيانات كاملة"}), 400
    
    result = orange_logic(num, pwd)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
