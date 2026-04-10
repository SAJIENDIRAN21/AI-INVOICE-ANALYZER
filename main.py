import os
import re
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw
from doctr.models import ocr_predictor
from doctr.io import DocumentFile

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load OCR model
ocr_model = ocr_predictor(pretrained=True)

def intelligent_parse(filepath):
    try:
        # OCR Processing
        doc = DocumentFile.from_images(filepath)
        ocr_result = ocr_model(doc)
        
        words_data = []
        for page in ocr_result.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        (x0, y0), (x1, y1) = word.geometry
                        words_data.append({
                            "text": word.value,
                            "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                            "center_y": (y0 + y1) / 2
                        })

        # Extracted results
        res = {
            "Company": "Not Found",
            "GST_Number": "Not Found",
            "Total_Amount": "Not Found",
            "Date": "Not Found"
        }

        full_text = " ".join([w["text"] for w in words_data])

        # Company Name (Header logic)
        header_words = [w["text"] for w in words_data if w["center_y"] < 0.12]
        clean_company = []
        for word in header_words:
            if word.upper() in ["TAX", "INVOICE", "BILL", "MEMO"]:
                break
            if word not in clean_company:
                clean_company.append(word)
        res["Company"] = " ".join(clean_company)

        # GST Extraction
        gst_match = re.search(r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}', full_text)
        if gst_match:
            res["GST_Number"] = gst_match.group(0)

        # Date Extraction
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text)
        if date_match:
            res["Date"] = date_match.group(0)

        # Total Amount (Anchor-based logic)
        total_anchor_y = None

        for w in words_data:
            if "GRAND" in w["text"].upper():
                total_anchor_y = w["center_y"]
                break

        if not total_anchor_y:
            for w in reversed(words_data):
                if "TOTAL" in w["text"].upper():
                    total_anchor_y = w["center_y"]
                    break

        if total_anchor_y:
            row_items = [w for w in words_data if abs(w["center_y"] - total_anchor_y) < 0.015]
            row_items.sort(key=lambda x: x["x0"], reverse=True)

            for item in row_items:
                price_match = re.search(r'(\d{1,3}(?:,\d{3})*\.\d{2})', item["text"])
                if price_match:
                    res["Total_Amount"] = f"₹{price_match.group(1)}"
                    break

        # Fallback logic
        if res["Total_Amount"] == "Not Found":
            footer_prices = []
            for w in words_data:
                if w["center_y"] > 0.6:
                    p_match = re.search(r'(\d{1,3}(?:,\d{3})*\.\d{2})', w["text"])
                    if p_match:
                        footer_prices.append(float(p_match.group(1).replace(',', '')))
            if footer_prices:
                res["Total_Amount"] = f"₹{max(footer_prices):,.2f}"

        # Draw bounding boxes (visual output)
        img = Image.open(filepath).convert("RGB")
        draw = ImageDraw.Draw(img)
        w_img, h_img = img.size

        for key, val in res.items():
            if val != "Not Found":
                for w in words_data:
                    if w["text"] in val:
                        draw.rectangle(
                            [w["x0"]*w_img, w["y0"]*h_img, w["x1"]*w_img, w["y1"]*h_img],
                            outline="red", width=3
                        )

        preview_filename = "preview_" + os.path.basename(filepath)
        img.save(os.path.join(UPLOAD_FOLDER, preview_filename))

        return res, preview_filename

    except Exception as e:
        return {"Error": str(e)}, None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploads/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/extract', methods=['POST'])
def extract():
    file = request.files.get('file')
    if not file:
        return "No file uploaded"

    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    output, preview_name = intelligent_parse(path)

    return render_template('index.html', summary=output, filename=preview_name)


if __name__ == '__main__':
    app.run(debug=True, port=5000)