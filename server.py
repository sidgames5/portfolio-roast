from flask import Flask, request, send_from_directory, jsonify
import requests
import ollama
import json

app = Flask(__name__, static_url_path="")
client = ollama.Client(host="http://10.0.1.152:11434")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)


@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")


@app.route("/api", methods=["POST"])
def api_endpoint():
    data = request.json
    html = ""
    res = requests.get(data["url"])
    if res.status_code == 200:
        html = res.text
    else:
        return "your portfolio so bad that i dont even know how to roast it"
    jsonres = client.chat(
        model="gemma:2b",
        messages=[
            {
                "role": "user",
                "content": f"I will provide the raw HTML of a developer portfolio site. Please roast the content of the website (dont comment about the actual code) and make your response super funny. Don't criticize it or suggest improvements, roast it, like put it on a grill until it is charred. Don't list the specific issues with the site, just slam the entire webpage in general. Also please make the point-of-view as if you are the one actually viewing the webpage and roasting it: f{html}",
            }
        ],
    )
    return jsonres["message"]["content"]


if __name__ == "__main__":
    app.run(debug=True)
