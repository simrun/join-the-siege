from flask import Flask, request, jsonify

from src.classifier import UnsupportedIndustryError, classify_file


app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 5 * 10**6  # 5 MB

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg'}

def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/classify_file', methods=['POST'])
def classify_file_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed"}), 415
    
    if 'industry' not in request.form:
        return jsonify({"error": "No industry part in the request"}), 400
    industry = request.form['industry']

    file_class = classify_file(file, industry)
    
    return jsonify({"file_class": file_class}), 200

@app.errorhandler(UnsupportedIndustryError)
def handle_unsupported_industry(e):
    return jsonify({"error": f"Unsupported industry: {e}"}), 422

if __name__ == '__main__':
    app.run(debug=True)
