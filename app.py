from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app) # للسماح بالاتصال من المتصفح

@app.route('/activate', methods=['POST'])
def activate():
    # استقبال البيانات من FormData
    number = request.form.get("phone")
    password = request.form.get("password")

    if not number or not password:
        return jsonify({"status": "error", "message": "Missing phone or password"}), 400

    # --- بداية كود أورنج الخاص بك بالحرف ---
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
        'Content-Type': "application/json; charset=UTF-8"}
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    try:
        AccessToken = response.json()['SignInUserResult']['AccessToken']
    except:
        return jsonify({"status": "error", "message": "رقم الهاتف أو كلمة المرور خطأ"})

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
    Token = response.json()["Token"]
    
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
        'X-Requested-With': "com.orange.mobinilandmf",
        'Origin': "https://services.orange.eg"}
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    data = response.json()
    
    if data.get('ErrorCode') == 1:
        return jsonify({"status": "error", "message": "انت دخلت علي الفوازير النهارده جرب بكره"})

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
    
    if response.json().get('ErrorDescription') == "FawazeerSuccess":
        return jsonify({"status": "success", "message": "تم إرسال 250 ميجا بنجاح"})
    else:
        return jsonify({"status": "error", "message": response.json().get('ErrorDescription', 'حدث خطأ غير معروف')})
    # --- نهاية كود أورنج ---

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
