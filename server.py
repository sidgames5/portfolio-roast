from flask import Flask, request, send_from_directory, jsonify
import requests
import ollama
import json
from urllib.parse import urlparse
import os

app = Flask(__name__, static_url_path="")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
client = ollama.Client(host=f"http://{OLLAMA_HOST}:11434")


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


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
    if not is_valid_url(data["url"]):
        return
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
