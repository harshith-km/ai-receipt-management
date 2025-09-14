# Smart Expense Tracker 🧾

A modern web application that uses OCR (Optical Character Recognition) and AI to automatically extract and categorize expenses from receipt images.

## Features

- 📸 **Receipt Upload**: Drag & drop or click to upload receipt images
- 🔍 **OCR Processing**: Extract text from images using Tesseract OCR
- 🤖 **AI Categorization**: Automatically categorize expenses (Food, Transport, Shopping, etc.)
- 📊 **Visual Analytics**: Interactive charts showing spending breakdown
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

### Backend
- **Python Flask**: Web framework
- **Tesseract OCR**: Text extraction from images
- **OpenCV**: Image preprocessing for better OCR results
- **Pillow**: Image processing

### Frontend
- **React**: User interface
- **Chart.js**: Data visualization
- **Axios**: HTTP client
- **CSS3**: Modern styling with gradients and animations

## Installation

### Prerequisites
- Python 3.7+
- Node.js 14+
- Tesseract OCR

#### Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Backend Setup

1. Navigate to the project directory:
```bash
cd /home/harsha/Parwana
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
cd backend
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Upload Receipt**: Click the upload area or drag & drop a receipt image
2. **Process**: Click "Process Receipt" to extract and categorize expenses
3. **View Results**: See the categorized expenses, totals, and visual charts
4. **Analyze**: Review spending patterns and category breakdowns

## API Endpoints

### POST /api/upload
Upload and process a receipt image.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Image file

**Response:**
```json
{
  "success": true,
  "items": [
    {
      "name": "Coffee",
      "amount": 4.50,
      "category": "Food"
    }
  ],
  "total_amount": 25.75,
  "category_totals": {
    "Food": 15.25,
    "Transport": 10.50
  },
  "extracted_text": "Raw OCR text...",
  "receipt_date": "2024-01-15T10:30:00"
}
```

### GET /api/health
Health check endpoint.

## Expense Categories

The AI automatically categorizes expenses into:

- 🍕 **Food**: Restaurants, groceries, cafes
- 🚗 **Transport**: Gas, taxi, parking, tolls
- 🛍️ **Shopping**: Clothing, electronics, gifts
- 🏥 **Healthcare**: Pharmacy, medical expenses
- 🎬 **Entertainment**: Movies, games, concerts
- ⚡ **Utilities**: Bills, internet, phone
- 📦 **Other**: Uncategorized items

## Image Processing

The application includes advanced image preprocessing:

1. **Grayscale Conversion**: Reduces noise
2. **Gaussian Blur**: Smooths the image
3. **Threshold Processing**: Creates binary image for better OCR
4. **Text Extraction**: Uses Tesseract for OCR
5. **Data Parsing**: Extracts amounts and item names

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is installed and in PATH
2. **Poor OCR results**: Try higher quality images with better contrast
3. **CORS errors**: Make sure both servers are running on correct ports
4. **File upload fails**: Check file size and format (JPG, PNG recommended)

### Improving OCR Accuracy

- Use high-resolution images (300+ DPI)
- Ensure good lighting and contrast
- Avoid blurry or rotated images
- Clean, flat receipts work best

## Development

### Project Structure
```
Parwana/
├── backend/
│   ├── app.py              # Flask application
│   └── uploads/            # Temporary file storage
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Styles
│   └── package.json        # Node dependencies
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Adding New Categories

Edit the `EXPENSE_CATEGORIES` dictionary in `backend/app.py`:

```python
EXPENSE_CATEGORIES = {
    'food': ['food', 'restaurant', 'grocery', ...],
    'your_category': ['keyword1', 'keyword2', ...],
    # ...
}
```

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Future Enhancements

- 📱 Mobile app version
- 🔄 Batch processing multiple receipts
- 📈 Historical spending trends
- 💾 Database integration for expense storage
- 🔐 User authentication and personal accounts
- 📧 Email receipt processing
- 🌐 Multi-language OCR support
