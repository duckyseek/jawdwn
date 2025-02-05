from flask import Flask, request, jsonify
import easyocr
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

# Initialize EasyOCR reader
easyocr_reader = easyocr.Reader(['en'])

# Initialize DocTR predictor
doctr_predictor = ocr_predictor(pretrained=True)

def load_image(image_source):
    """
    Load an image from a file or URL.
    """
    try:
        if isinstance(image_source, str) and image_source.startswith(('http://', 'https://')):
            response = requests.get(image_source)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_source)
        return image.convert('RGB')
    except Exception as e:
        raise ValueError(f"Error loading image: {e}")

def ocr_easyocr(image):
    """
    Perform OCR using EasyOCR.
    """
    try:
        results = easyocr_reader.readtext(image, detail=0)
        return results
    except Exception as e:
        raise ValueError(f"EasyOCR processing error: {e}")

def ocr_doctr(image):
    """
    Perform OCR using DocTR.
    """
    try:
        doc = doctr_predictor(DocumentFile.from_images(image))
        results = []
        for page in doc.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = ' '.join(word.value for word in line.words)
                    results.append(line_text)
        return results
    except Exception as e:
        raise ValueError(f"DocTR processing error: {e}")

@app.route('/ocr', methods=['POST'])
def ocr():
    """
    Endpoint to process an image and return OCR results from both EasyOCR and DocTR.
    """
    if 'image' not in request.files and 'image_url' not in request.json:
        return jsonify({"error": "No image provided. Use 'image' field in form-data or 'image_url' in JSON."}), 400

    try:
        if 'image' in request.files:
            image = load_image(request.files['image'])
        else:
            image_url = request.json['image_url']
            image = load_image(image_url)

        # Perform OCR with EasyOCR
        easyocr_text = ocr_easyocr(image)

        # Perform OCR with DocTR
        doctr_text = ocr_doctr(image)

        return jsonify({
            "easyocr_text": easyocr_text,
            "doctr_text": doctr_text
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the OCR API. Use the /ocr endpoint to process images."})

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "OCR API is running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
