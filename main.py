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
            clean_id = raw_id.replace("t_", "").replace("t", "") if raw_id else "N/A"  # Remove t or t_
            gc_list.append({
                "gc_name": gc.get("name", "Unknown"),
                "gc_uid": clean_id
            })
        return gc_list
    else:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>GC UID Finder</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');

    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(to right, #9932CC, #FF00FF, #F6358A);
      color: #f5f5f5;
      margin: 0;
      padding: 0;
      text-align: center;
    }

    .header, .footer {
      background: linear-gradient(to right, #9932CC, #FF00FF);
      padding: 15px;
      margin: auto;
      font-size: 16px;
      width: 92%;
      border-radius: 10px;
      box-shadow: 0 0 5px #ff00cc, 0 0 10px #6600ff;
      margin-top: 30px;
    }

    .container {
      width: 92%;
      max-width: 320px;
      margin: 30px auto;
      background: linear-gradient(to right, #9932CC, #FF00FF);
      padding: 25px;
      border-radius: 20px;
      box-shadow: 0 0 10px #8000ff, 0 0 20px #ff00cc, inset 0 0 10px #330033;
    }

    input {
      width: 100%;
      padding: 12px;
      border-radius: 10px;
      border: none;
      background-color: white;
      color: white;
      margin-bottom: 15px;
      outline: none;
      font-size: 14px;
    }

    .btn {
      background: linear-gradient(145deg, #6600ff, #ff00cc);
      color: white;
      padding: 12px;
      width: 100%;
      border: none;
      border-radius: 10px;
      font-size: 15px;
      cursor: pointer;
      margin-top: 10px;
      box-shadow: 0 0 10px #6600ff;
      transition: 0.3s ease;
    }

    .btn:hover {
      background: linear-gradient(145deg, #ff00cc, #ffffff);
      color: black;
    }

    .box {
      background: #2f2f2f;
      padding: 15px;
      margin-top: 15px;
      border-radius: 12px;
      box-shadow: 0 0 10px rgba(255, 0, 255, 0.3);
      text-align: left;
      font-family: Arial, sans-serif;
    }

    .copy-btn {
      margin-top: 5px;
      padding: 5px 10px;
      border: none;
      border-radius: 8px;
      background: #6600ff;
      color: white;
      cursor: pointer;
      font-size: 12px;
    }

    .copy-btn:hover {
      background: #ff00cc;
    }

    .spinner {
      margin-top: 10px;
      border: 4px solid #333;
      border-top: 4px solid #ff00cc;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      animation: spin 1s linear infinite;
      display: inline-block;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    @media (max-width: 600px) {
      .container { width: 94%; }
      .header, .footer { width: 90%; }
    }
  </style>
</head>
<body>
  <div class="header">TOKEN & GC UID FINDER PANEL</div>

  <div class="container">
    <h3>Enter Token Below</h3>
    <input type="text" id="token" placeholder="Paste Facebook Token"/>
    <button class="btn" onclick="fetchTokenInfo()">Check Token</button>
    <button class="btn" onclick="fetchGcUids()">Find GC UID</button>

    <div id="tokenResult" class="box"></div>
    <div id="gcResult" class="box"></div>
    <div id="loading" style="display: none;" class="spinner"></div>
  </div>

  <div class="footer">The Tool Made By Henry </div>

  <script>
    function fetchTokenInfo() {
      const token = document.getElementById("token").value.trim();
      if (!token) return alert("Please enter a token!");

      document.getElementById("loading").style.display = "inline-block";
      fetch("/token_info", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "token=" + encodeURIComponent(token)
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById("loading").style.display = "none";
        const result = document.getElementById("tokenResult");
        result.innerHTML = data.error
          ? `<p style="color:red;">❌ ${data.error}</p>`
          : `
            <h3>✅ Token Info</h3>
            <p><strong>Name:</strong> ${data.name}</p>
            <p><strong>ID:</strong> ${data.id}</p>
            <p><strong>DOB:</strong> ${data.dob}</p>
            <p><strong>Email:</strong> ${data.email}</p>
          `;
      });
    }

    function fetchGcUids() {
      const token = document.getElementById("token").value.trim();
      if (!token) return alert("Please enter a token!");

      document.getElementById("loading").style.display = "inline-block";
      fetch("/gc_uid", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "token=" + encodeURIComponent(token)
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById("loading").style.display = "none";
        const result = document.getElementById("gcResult");
        result.innerHTML = `<h3>Messenger Group Chats</h3>`;

        if (data.error) {
          result.innerHTML += `<p style="color:red;">❌ ${data.error}</p>`;
        } else {
          data.gc_data.forEach((gc, i) => {
            const gcBlock = document.createElement("div");
            gcBlock.classList.add("box");
            gcBlock.innerHTML = `
              <p><strong>GC ${i + 1}:</strong></p>
              <p><strong>Name:</strong> ${gc.gc_name}</p>
              <p><strong>UID:</strong> ${gc.gc_uid}</p>
              <button class="copy-btn" onclick="copyToClipboard('${gc.gc_uid}')">Copy UID</button>
            `;
            result.appendChild(gcBlock);
          });
        }
      });
    }

    function copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        alert("✅ UID copied to clipboard!");
      });
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
