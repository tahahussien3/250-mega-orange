from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- Manual CORS Fix (No library needed) ---
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def orange_logic(number, password):
    session = requests.Session()
    signin_url = "https://services.orange.eg/SignIn.svc/SignInUser"
    payload = {
        "appVersion": "9.0.1",
        "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
        "dialNumber": number,
        "isAndroid": True,
        "lang": "ar",
        "password": password
    }
    
    try:
        # Step 1: Login
        res = session.post(signin_url, json=payload, timeout=20)
        auth_data = res.json()
        
        if 'SignInUserResult' not in auth_data or 'AccessToken' not in auth_data['SignInUserResult']:
            return {"status": "error", "message": "Invalid number or password."}
            
        access_token = auth_data['SignInUserResult']['AccessToken']

        # Step 2: Token Generation
        gen_url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        gen_payload = {
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number,
            "Language": "ar",
            "Module": "0",
            "Password": password
        }
        token_res = session.post(gen_url, json=gen_payload, headers={'Token': access_token})
        final_token = token_res.json().get("Token")

        # Step 3: Fetch Questions
        q_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        q_data = session.post(q_url, json={"Dial": number, "Language": "ar", "Token": final_token}).json()
        
        if q_data.get('ErrorCode') == 1:
            return {"status": "error", "message": "Already claimed today."}

        # Step 4: Submit Correct Answers
        answers_list = []
        for q in q_data.get("Questions", []):
            for a in q.get("Answers", []):
                if a.get("IsCorrect"):
                    answers_list.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                    break

        sub_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        sub_res = session.post(sub_url, json={"Dial": number, "Language": "ar", "Token": final_token, "Answers": answers_list})
        
        if sub_res.json().get('ErrorDescription') == "FawazeerSuccess":
            return {"status": "success", "message": "Done! 250 MB sent."}
        
        return {"status": "error", "message": sub_res.json().get('ErrorDescription', 'Operation failed')}

    except Exception as e:
        # Returning technical error for better debugging during migration
        return {"status": "error", "message": f"Connection Error: {str(e)}"}

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
    # CRITICAL: Railway uses the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
