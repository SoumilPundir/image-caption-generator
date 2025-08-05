import os
import io
import base64
import traceback
from flask import Flask, render_template, request, jsonify
from PIL import Image
import torch
from transformers import pipeline

app = Flask(__name__)

# Create image captioning pipeline
try:
    # Use a more robust pre-trained model
    captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
except Exception as e:
    print(f"Error loading model: {e}")
    captioner = None

def decode_image(image_data):
    """
    Decode base64 or handle file upload
    """
    try:
        # If it's a base64 string
        if isinstance(image_data, str):
            # Remove data URL prefix if exists
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        
        # If it's a file storage object
        else:
            image = Image.open(image_data)
        
        return image
    except Exception as e:
        print(f"Image decoding error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_caption', methods=['POST'])
def generate_caption():
    try:
        # Check if model is loaded
        if captioner is None:
            return jsonify({
                'success': False, 
                'message': 'Image captioning model failed to load'
            }), 500

        # Get image from request
        if 'image_url' in request.json and request.json['image_url']:
            # Download image from URL
            import requests
            response = requests.get(request.json['image_url'])
            image = Image.open(io.BytesIO(response.content))
        
        elif 'image_base64' in request.json and request.json['image_base64']:
            # Decode base64 image
            image = decode_image(request.json['image_base64'])
        
        else:
            return jsonify({
                'success': False, 
                'message': 'No image provided'
            }), 400

        # Generate caption
        if image:
            captions = captioner(image)
            
            # Return the first (most likely) caption
            caption = captions[0]['generated_text'] if captions else 'No caption generated'
            
            return jsonify({
                'success': True,
                'caption': caption
            })
        
        return jsonify({
            'success': False, 
            'message': 'Invalid image'
        }), 400

    except Exception as e:
        print(f"Error generating caption: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 500

# Diagnostic route
@app.route('/diagnostic')
def diagnostic():
    """
    Simple diagnostic route to check application status
    """
    return jsonify({
        'model_loaded': captioner is not None,
        'torch_cuda_available': torch.cuda.is_available(),
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}"
    })

if __name__ == '__main__':
    app.run(debug=True)