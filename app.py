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

    if not number or not password:
        return jsonify({
            "status": "fail",
            "message": "لازم تدخل رقم الموبايل وكلمة السر"
        }), 400

    # ---------------- LOGIN ----------------
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
        "password": password
    }

    headers = {
        'User-Agent': "okhttp/4.10.0",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json; charset=UTF-8"
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print("\n=== LOGIN RESPONSE ===")
    print("STATUS:", response.status_code)
    print("TEXT:", response.text)

    try:
        AccessToken = response.json()['SignInUserResult']['AccessToken']
    except:
        return jsonify({
            "status": "fail",
            "message": "رقم الموبايل أو كلمة السر غلط"
        }), 401

    # ---------------- GENERATE TOKEN ----------------
    url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
    payload = {
        "ChannelName": "MobinilAndMe",
        "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
        "Dial": number,
        "Language": "ar",
        "Module": "0",
        "Password": password
    }

    headers.update({
        'AppVersion': "9.0.1",
        'OsVersion': "13",
        'IsAndroid': "true",
        'IsEasyLogin': "false",
        'Token': AccessToken
    })

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print("\n=== GENERATE TOKEN RESPONSE ===")
    print("STATUS:", response.status_code)
    print("TEXT:", response.text)

    try:
        Token = response.json().get("Token")
    except:
        return jsonify({
            "status": "fail",
            "message": "مشكلة في السيرفر الخارجي"
        }), 500

    # ---------------- GET QUESTIONS ----------------
    url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
    payload = {
        "Dial": number,
        "Language": "ar",
        "Token": Token
    }

    headers.update({
        'User-Agent': "Mozilla/5.0",
        'Accept': "application/json, text/plain, */*"
    })

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print("\n=== QUESTIONS RESPONSE ===")
    print("STATUS:", response.status_code)
    print("TEXT:", response.text)

    try:
        data = response.json()
    except:
        return jsonify({
            "status": "fail",
            "message": "السيرفر الخارجي مش بيرد"
        }), 500

    if data.get('ErrorCode') == 1:
        return jsonify({
            "status": "fail",
            "message": "انت استخدمت العرض النهارده، جرب بكرة"
        }), 200

    questions = data.get("Questions", [])
    answers_list = []

    for q in questions:
        for a in q["Answers"]:
            if a["IsCorrect"] == True:
                answers_list.append({
                    "QuestionId": a["QuestionId"],
                    "AnswerId": a["Id"]
                })
                break

    # ---------------- SUBMIT ----------------
    url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
    payload = {
        "Dial": number,
        "Language": "ar",
        "Token": Token,
        "Answers": answers_list
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print("\n=== SUBMIT RESPONSE ===")
    print("STATUS:", response.status_code)
    print("TEXT:", response.text)

    try:
        result = response.json()
    except:
        return jsonify({
            "status": "fail",
            "message": "مشكلة أثناء إرسال الإجابات"
        }), 500

    error = result.get('ErrorDescription')

    if error == "FawazeerSuccess":
        message = "تم إضافة 250 ميجا بنجاح 🔥"
        status = "success"

    elif error == "GiftCapped":
        message = "تم استهلاك الحد الأقصى للهدايا 😅"
        status = "fail"

    else:
        message = "حصل خطأ: " + str(error)
        status = "fail"

    return jsonify({
        "status": status,
        "message": message
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
