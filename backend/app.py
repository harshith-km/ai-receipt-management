import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import cv2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

is_processing = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# -------- OCR Helper --------
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed_path = image_path.replace('.', '_processed.')
    cv2.imwrite(processed_path, thresh)
    return processed_path

def extract_text_from_image(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        if text.strip():
            return text
        processed_path = preprocess_image(image_path)
        text = pytesseract.image_to_string(Image.open(processed_path))
        if os.path.exists(processed_path):
            os.remove(processed_path)
        return text
    except Exception:
        return ""

# -------- Simple Parser (Fallback) --------
def parse_receipt_simple(text):
    """Simple receipt parser as fallback when AI is not available"""
    import re
    
    print(f"Simple parser processing: {repr(text)}")
    lines = text.split('\n')
    items = []
    total_amount = 0
    
    # Patterns for amounts
    amount_patterns = [
        r'₹?(\d+\.?\d*)',   # ₹450 or 450
        r'Rs\.?\s*(\d+\.?\d*)',  # Rs. 450 or Rs 450
        r'(\d+\.?\d*)',     # Just numbers: 450.50
        r'(\d+)',           # Whole numbers: 450
    ]
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue
            
        # Try different amount patterns
        amounts = []
        for pattern in amount_patterns:
            amounts = re.findall(pattern, line)
            if amounts:
                break
        
        if amounts:
            try:
                amount = float(amounts[-1])
                print(f"Found amount: {amount} in line: {line}")
                # For INR, amounts are usually larger (like 50, 25, 75)
                if amount < 1:  # Skip very small amounts
                    continue
                    
                # Extract item name
                item_name = re.sub(r'₹?(\d+\.?\d*)', '', line).strip()
                item_name = re.sub(r'Rs\.?\s*(\d+\.?\d*)', '', item_name).strip()
                item_name = re.sub(r'[^\w\s-]', '', item_name).strip()
                
                # Clean up common OCR errors
                item_name = item_name.replace('Coffes', 'Coffee')
                item_name = item_name.replace('Bgel', 'Bagel')
                item_name = item_name.replace('Tout', 'Total')
                
                if item_name and amount > 0:
                    # Simple categorization
                    category = 'Other'
                    item_lower = item_name.lower()
                    if any(word in item_lower for word in ['coffee', 'food', 'restaurant', 'cafe']):
                        category = 'Food'
                    elif any(word in item_lower for word in ['gas', 'fuel', 'taxi', 'transport']):
                        category = 'Transport'
                    elif any(word in item_lower for word in ['shop', 'store', 'clothing']):
                        category = 'Shopping'
                    
                    items.append({
                        'name': item_name,
                        'amount': amount,
                        'category': category
                    })
                    
                    if amount > total_amount:
                        total_amount = amount
                        
            except ValueError:
                continue
    
    return {
        'items': items,
        'total_amount': total_amount
    }

# -------- AI Helper --------
def analyze_text_with_gemini(extracted_text):
    prompt_text = f"""
    You are a financial assistant. Analyze the following receipt text and return ONLY a JSON object with this exact structure:
    {{
      "items": [
        {{ "name": "item_name", "amount": 0.0, "category": "category_name" }}
      ],
      "total_amount": 0.0
    }}
    
    Categories: Food, Transport, Shopping, Healthcare, Entertainment, Utilities, Other.
    Receipt Text:
    {extracted_text}
    """
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    
    # Extract the text from Gemini response
    gemini_response = response.json()
    try:
        # Get the generated text from Gemini
        generated_text = gemini_response['candidates'][0]['content']['parts'][0]['text']
        print(f"Gemini response: {repr(generated_text)}")
        
        # Clean up the response text (remove markdown formatting if present)
        cleaned_text = generated_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        # Parse the JSON from the generated text
        return json.loads(cleaned_text)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing Gemini response: {e}")
        print(f"Raw response: {gemini_response}")
        # Return default structure if parsing fails
        return {
            "items": [],
            "total_amount": 0.0
        }

# -------- Upload Endpoint --------
@app.route('/api/upload', methods=['POST'])
def upload_receipt():
    global is_processing
    if is_processing:
        return jsonify({'error': 'Another receipt is being processed. Please wait.'}), 429
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    is_processing = True
    try:
        filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)

        # Extract text from image
        extracted_text = extract_text_from_image(filepath)
        print(f"Extracted text: {repr(extracted_text)}")
        if not extracted_text.strip():
            return jsonify({'error': 'Could not extract text from image'}), 400

        # Try Gemini AI first, fallback to simple parsing
        try:
            if GEMINI_API_KEY and GEMINI_API_KEY != "your_api_key_here" and GEMINI_API_KEY.strip():
                print("Using Gemini AI for analysis")
                ai_response = analyze_text_with_gemini(extracted_text)
            else:
                print("Using simple parser (no valid Gemini API key)")
                ai_response = parse_receipt_simple(extracted_text)
        except Exception as e:
            print(f"AI analysis failed: {e}")
            # Fallback to simple parsing
            ai_response = parse_receipt_simple(extracted_text)

        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'ai_analysis': ai_response
        })

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    finally:
        is_processing = False
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Smart Expense Tracker API is running'})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
