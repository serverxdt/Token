from flask import Flask, request, render_template_string
import requests

# Flask app initialization
app = Flask(__name__)

# HTML template for the stylish interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Token Validator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f3f3f3;
            color: #333;
            text-align: center;
            padding: 20px;
        }
        h1 {
            color: #4CAF50;
        }
        input[type="text"], textarea {
            width: 90%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #45a049;
        }
        .result {
            margin-top: 20px;
            text-align: left;
            background: #fff;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            display: inline-block;
        }
        .valid {
            color: green;
            font-weight: bold;
        }
        .invalid {
            color: red;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Facebook Token Validator</h1>
    <form method="POST" action="/validate" enctype="multipart/form-data">
        <textarea name="tokens" placeholder="Enter tokens here, one per line..." rows="8"></textarea>
        <br>
        <button type="submit">Validate Tokens</button>
    </form>
    <div class="result">
        {% if results %}
            {% for token, data in results.items() %}
                <p><span>{{ token }}</span>: 
                {% if data['status'] == 'Valid' %}
                    <span class="valid">{{ data['status'] }}</span>
                    <br>
                    Name: <b>{{ data['name'] }}</b><br>
                    ID: <b>{{ data['id'] }}</b><br>
                    Email: <b>{{ data['email'] or 'N/A' }}</b>
                {% else %}
                    <span class="invalid">{{ data['status'] }}</span>
                {% endif %}
                </p>
            {% endfor %}
        {% endif %}
    </div>
</body>
</html>
"""

# Token validation function with more details
def validate_token(token):
    url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={token}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "Valid",
                "id": data.get("id"),
                "name": data.get("name"),
                "email": data.get("email")
            }
        else:
            return {"status": "Invalid", "id": None, "name": None, "email": None}
    except requests.RequestException:
        return {"status": "Invalid", "id": None, "name": None, "email": None}

# Route for the main page
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE)

# Route to validate tokens
@app.route("/validate", methods=["POST"])
def validate():
    tokens = request.form["tokens"].strip().split("\n")
    results = {}
    for token in tokens:
        token = token.strip()
        if token:
            results[token] = validate_token(token)
    return render_template_string(HTML_TEMPLATE, results=results)

# Run the app on localhost
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
