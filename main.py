from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

TOKEN_INFO_URL = "https://graph.facebook.com/v17.0/me?fields=id,name,birthday,email"
GC_UID_URL = "https://graph.facebook.com/v17.0/me/conversations?fields=id,name"

def check_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(TOKEN_INFO_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return {
            "status": "Valid",
            "name": data.get("name", "N/A"),
            "id": data.get("id", "N/A"),
            "dob": data.get("birthday", "N/A"),
            "email": data.get("email", "N/A")
        }
    else:
        return {"status": "Invalid"}

def get_gc_details(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(GC_UID_URL, headers=headers)
    if response.status_code == 200:
        gc_data = response.json().get("data", [])
        gc_list = []
        for gc in gc_data:
            raw_id = gc.get("id", "N/A")
            clean_id = raw_id.replace("t_", "").replace("t", "") if raw_id else "N/A"
            gc_list.append({
                "gc_name": gc.get("name", "Unknown"),
                "gc_uid": clean_id
            })
        return gc_list
    return None


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>2025 GC UID Finder</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');

    body {
      font-family: 'Orbitron', sans-serif;
      background: radial-gradient(circle at top, #ff00ff, #6600ff, #000000);
      color: #fff;
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }

    .glass-container {
      background: rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 20px;
      padding: 25px;
      width: 90%;
      max-width: 420px;
      box-shadow: 0 0 25px rgba(255, 0, 255, 0.5);
      text-align: center;
      animation: popUp 0.8s ease-out;
    }

    @keyframes popUp {
      from { transform: scale(0.8); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }

    h1 {
      margin-bottom: 10px;
      font-size: 22px;
      text-shadow: 0 0 10px #ff00ff;
    }

    input {
      width: 95%;
      padding: 12px;
      border-radius: 12px;
      border: none;
      outline: none;
      margin-bottom: 15px;
      font-size: 14px;
      text-align: center;
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
      box-shadow: inset 0 0 10px rgba(255, 0, 255, 0.3);
    }

    input::placeholder { color: #ddd; }

    .btn {
      display: block;
      width: 100%;
      background: linear-gradient(90deg, #ff00ff, #6600ff);
      color: white;
      border: none;
      border-radius: 12px;
      padding: 12px;
      font-size: 15px;
      margin: 8px 0;
      cursor: pointer;
      box-shadow: 0 0 12px #ff00ff;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .btn:hover {
      transform: scale(1.05);
      box-shadow: 0 0 20px #ff00ff, 0 0 40px #6600ff;
    }

    .result-box {
      background: rgba(0, 0, 0, 0.4);
      border-radius: 12px;
      padding: 10px;
      margin-top: 12px;
      text-align: left;
      box-shadow: inset 0 0 10px rgba(255, 0, 255, 0.3);
    }

    .copy-btn {
      background: #ff00ff;
      color: white;
      border: none;
      border-radius: 8px;
      padding: 6px 10px;
      cursor: pointer;
      font-size: 12px;
      margin-top: 5px;
      transition: 0.2s ease;
    }

    .copy-btn:hover {
      background: #ffffff;
      color: #6600ff;
    }

    .spinner {
      margin: 15px auto;
      border: 4px solid rgba(255, 255, 255, 0.2);
      border-top: 4px solid #ff00ff;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
    }

    @keyframes spin { 100% { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <div class="glass-container">
    <h1>⚡ 2025 GC UID Finder</h1>
    <input type="text" id="token" placeholder="Paste Your Facebook Token"/>
    <button class="btn" onclick="fetchTokenInfo()">🔑 Check Token</button>
    <button class="btn" onclick="fetchGcUids()">💬 Find GC UID</button>

    <div id="loading" class="spinner" style="display: none;"></div>
    <div id="tokenResult" class="result-box"></div>
    <div id="gcResult" class="result-box"></div>
  </div>

  <script>
    function fetchTokenInfo() {
      const token = document.getElementById("token").value.trim();
      if (!token) return alert("Please enter a token!");
      toggleLoading(true);

      fetch("/token_info", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "token=" + encodeURIComponent(token)
      })
      .then(res => res.json())
      .then(data => {
        toggleLoading(false);
        const result = document.getElementById("tokenResult");
        result.innerHTML = data.error
          ? `<p style="color:#ff4444;">❌ ${data.error}</p>`
          : `<p><b>✅ Name:</b> ${data.name}</p>
             <p><b>ID:</b> ${data.id}</p>
             <p><b>DOB:</b> ${data.dob}</p>
             <p><b>Email:</b> ${data.email}</p>`;
      });
    }

    function fetchGcUids() {
      const token = document.getElementById("token").value.trim();
      if (!token) return alert("Please enter a token!");
      toggleLoading(true);

      fetch("/gc_uid", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "token=" + encodeURIComponent(token)
      })
      .then(res => res.json())
      .then(data => {
        toggleLoading(false);
        const result = document.getElementById("gcResult");
        result.innerHTML = `<h3>Messenger Group Chats</h3>`;
        if (data.error) {
          result.innerHTML += `<p style="color:#ff4444;">❌ ${data.error}</p>`;
        } else {
          data.gc_data.forEach((gc, i) => {
            result.innerHTML += `
              <div style="margin-top:10px; border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:8px;">
                <p><b>GC ${i+1}:</b> ${gc.gc_name}</p>
                <p><b>UID:</b> ${gc.gc_uid}</p>
                <button class="copy-btn" onclick="copyToClipboard('${gc.gc_uid}')">📋 Copy UID</button>
              </div>`;
          });
        }
      });
    }

    function copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => alert("✅ UID copied!"));
    }

    function toggleLoading(show) {
      document.getElementById("loading").style.display = show ? "block" : "none";
    }
  </script>
</body>
</html>
    """)


@app.route("/token_info", methods=["POST"])
def token_info():
    token = request.form.get("token").strip()
    if not token:
        return jsonify({"error": "Token is required!"})
    token_info = check_token(token)
    if token_info["status"] == "Invalid":
        return jsonify({"error": "Invalid or expired token!"})
    return jsonify(token_info)

@app.route("/gc_uid", methods=["POST"])
def gc_uid():
    token = request.form.get("token").strip()
    if not token:
        return jsonify({"error": "Token is required!"})
    gc_data = get_gc_details(token)
    if gc_data is None:
        return jsonify({"error": "Failed to fetch GC UIDs!"})
    return jsonify({"gc_data": gc_data})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
