from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route("/activate", methods=["POST"])
def activate():
    data = request.json

    number = data.get("number")
    password = data.get("password")

    if not number or not password:
        return jsonify({"error": "number and password required"}), 400

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

    try:
        AccessToken = response.json()['SignInUserResult']['AccessToken']
    except:
        return jsonify({"error": "Number or password error"}), 401

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
    Token = response.json().get("Token")

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
    data = response.json()

    if data.get('ErrorCode') == 1:
        return jsonify({"message": "already used today"}), 200

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
    result = response.json()

    if result.get('ErrorDescription') == "FawazeerSuccess":
        return jsonify({"status": "success", "message": "Done send 250 mg"})
    else:
        return jsonify({"status": "fail", "message": result.get('ErrorDescription')})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
