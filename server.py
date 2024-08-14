from flask import Flask, request, send_from_directory, jsonify
import requests
import ollama

app = Flask(__name__, static_url_path="")


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
    result = ollama.chat(
        model="gemma:2b",
        messages=[
            {
                "role": "user",
                "content": f"I will provide the raw HTML of a developer portfolio site. Please roast the content (not the actual code) and make your response super funny. Don't criticize it, roast it, like put it on a grill until it is charred: f{html}",
            }
        ],
    )
    # TODO: the result is just json it needs to be decoded
    return result


if __name__ == "__main__":
    app.run(debug=True)
