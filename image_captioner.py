import torch
from transformers import VisionEncoderDecoderModel, AutoImageProcessor, AutoTokenizer
from PIL import Image
import requests
from io import BytesIO
import base64
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

class ImageCaptioner:
    def __init__(self, model_name="nlpconnect/vit-gpt2-image-captioning"):
        """
        Initialize image captioning model with updated processing
        """
        try:
            self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
            
            self.image_processor = AutoImageProcessor.from_pretrained(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)

            self.max_length = 16
            self.num_beams = 4
            self.gen_kwargs = {
                "max_length": self.max_length, 
                "num_beams": self.num_beams,
                "early_stopping": True
            }
        
        except Exception as e:
            print(f"Error initializing model: {e}")
            raise
    
    def _prepare_image(self, image):
        """
        Standardize image preparation process
        """
        if image.mode != "RGB":
            image = image.convert(mode="RGB")

        inputs = self.image_processor(images=image, return_tensors="pt")
        pixel_values = inputs.pixel_values.to(self.device)
        
        return pixel_values
    
    def caption_from_base64(self, base64_image):
        """
        Generate caption from base64 encoded image
        """
        try:
            image_data = base64.b64decode(base64_image.split(',')[1])
            image = Image.open(BytesIO(image_data))
            

            pixel_values = self._prepare_image(image)
            

            output_ids = self.model.generate(pixel_values, **self.gen_kwargs)
            pred = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            
            return pred.strip()
        
        except Exception as e:
            return f"Error processing base64 image: {str(e)}"
    
    def caption_from_url(self, image_url):
        """
        Generate caption for an image from a URL
        """
        try:

            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
     
            pixel_values = self._prepare_image(image)
            

            output_ids = self.model.generate(pixel_values, **self.gen_kwargs)
            pred = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            
            return pred.strip()
        
        except Exception as e:
            return f"Error downloading/processing image: {str(e)}"

def check_model_availability():
    """
    Check if the model can be loaded successfully
    """
    try:
        captioner = ImageCaptioner()
        print("Model loaded successfully!")
        return True
    except Exception as e:
        print(f"Model loading failed: {e}")
        return False

# Run diagnostic check
if __name__ == "__main__":
    check_model_availability()
