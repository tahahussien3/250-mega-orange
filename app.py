from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # استخدام مكتبة CORS أسهل وأضمن

def orange_logic(number, password):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
    })

    try:
        # الخطوة 1: تسجيل الدخول
        signin_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {
            "appVersion": "9.0.1",
            "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
            "dialNumber": number,
            "isAndroid": True,
            "lang": "ar",
            "password": password
        }
        
        res = session.post(signin_url, json=payload, timeout=20)
        auth_data = res.json()

        if 'SignInUserResult' not in auth_data or 'AccessToken' not in auth_data['SignInUserResult']:
            return {"status": "error", "message": "رقم الهاتف أو كلمة السر خطأ", "raw": auth_data}
            
        access_token = auth_data['SignInUserResult']['AccessToken']

        # الخطوة 2: توليد التوكن النهائي
        gen_url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        gen_payload = {
            "ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number, "Language": "ar", "Module": "0", "Password": password
        }
        token_res = session.post(gen_url, json=gen_payload, headers={'Token': access_token}, timeout=20)
        
        try:
            final_token = token_res.json().get("Token")
            if not final_token:
                return {"status": "error", "message": "فشل توليد توكن الدخول", "raw": token_res.json()}
        except:
            return {"status": "error", "message": "خطأ في استلام التوكن", "raw": token_res.text}

        # الخطوة 3: جلب الأسئلة
        q_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        q_res = session.post(q_url, json={"Dial": number, "Language": "ar", "Token": final_token}, timeout=20)
        q_data = q_res.json()
        
        if q_data.get('ErrorCode') == 1:
            return {"status": "error", "message": "استنفدت محاولات اليوم", "raw": q_data}

        questions = q_data.get("Questions", [])
        if not questions:
            return {"status": "error", "message": "لا توجد عروض متاحة حالياً", "raw": q_data}

        # الخطوة 4: الإجابات
        answers_list = []
        for q in questions:
            for a in q.get("Answers", []):
                if a.get("IsCorrect"):
                    answers_list.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                    break

        # الخطوة 5: الإرسال النهائي
        sub_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        sub_res = session.post(sub_url, json={"Dial": number, "Language": "ar", "Token": final_token, "Answers": answers_list}, timeout=20)
        
        result_data = sub_res.json()
        if result_data.get('ErrorDescription') == "FawazeerSuccess":
            return {"status": "success", "message": "مبروك! تم تفعيل 250 ميجا هدية.", "raw": result_data}
        
        return {"status": "error", "message": "فشلت عملية تفعيل الهدية", "raw": result_data}

    except Exception as e:
        return {"status": "error", "message": "حدث خطأ غير متوقع في السيرفر", "debug": str(e)}

@app.route('/activate', methods=['POST'])
def activate():
    num = request.form.get('phone')
    pwd = request.form.get('password')
    
    if not num or not pwd:
        return jsonify({"status": "error", "message": "يرجى إدخال جميع البيانات"}), 400
        
    result = orange_logic(num, pwd)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
