from flask import Flask, request, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = "highlights"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():

    files = os.listdir(UPLOAD_FOLDER)

    if not files:
        return "No highlights uploaded yet"

    html = ""

    for file in files:

        html += f"""
        <video width="600" controls>
        <source src="/video/{file}" type="video/mp4">
        </video><br><br>
        """

    return html


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(save_path)

    print("Saved:", save_path)

    return "Upload successful"


@app.route("/video/<filename>")
def video(filename):

    return send_from_directory(UPLOAD_FOLDER, filename)


app.run(host="0.0.0.0", port=5000)