from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- إعدادات CORS للسماح بالاتصال من Netlify ---
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

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
        
        res = session.post(signin_url, json=payload, timeout=30)
        try:
            auth_data = res.json()
        except:
            return {"status": "error", "message": "Incorrect phone number or password."}

        if 'SignInUserResult' not in auth_data or 'AccessToken' not in auth_data['SignInUserResult']:
            return {"status": "error", "message": "Incorrect phone number or password."}
            
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
                return {"status": "error", "message": "الرقم او كلمة السر غلط."}
        except:
            return {"status": "error", "message": "الرقم او كلمة السر غلط."}

        # الخطوة 3: جلب الأسئلة (الفوازير)
        q_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        q_res = session.post(q_url, json={"Dial": number, "Language": "ar", "Token": final_token}, timeout=20)
        q_data = q_res.json()
        
        if q_data.get('ErrorCode') == 1:
            return {"status": "error", "message": "انت خدت العرض النهاردة قبل كده"}

        # الخطوة 4: تجميع الإجابات الصحيحة
        answers_list = []
        questions = q_data.get("Questions", [])
        if not questions:
            return {"status": "error", "message": "لا يوجد عروض متاحة اليوم"}

        for q in questions:
            for a in q.get("Answers", []):
                if a.get("IsCorrect"):
                    answers_list.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                    break

        # الخطوة 5: الإرسال النهائي للهدية
        sub_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        sub_res = session.post(sub_url, json={"Dial": number, "Language": "ar", "Token": final_token, "Answers": answers_list}, timeout=20)
        
        result_data = sub_res.json()
        if result_data.get('ErrorDescription') == "FawazeerSuccess":
            return {"status": "success", "message": "تم تفعيل 250 ميجا هدية."}
        
        return {"status": "error", "message": result_data.get('ErrorDescription', 'Operation failed')}

    except Exception:
        return {"status": "error", "message": "الخدمة غير متاحة الان حاول وقت تانى"}

@app.route('/activate', methods=['POST', 'OPTIONS'])
def activate():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    num = request.form.get('phone')
    pwd = request.form.get('password')
    
    if not num or not pwd:
        return jsonify({"status": "error", "message": "Missing input"}), 400
        
    result = orange_logic(num, pwd)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)