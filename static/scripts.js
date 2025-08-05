document.addEventListener('DOMContentLoaded', () => {
    const imageUpload = document.getElementById('image-upload');
    const imageUrl = document.getElementById('image-url');
    const previewImage = document.getElementById('preview-image');
    const generateButton = document.getElementById('generate-caption');
    const captionResult = document.getElementById('caption-result');

    imageUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                previewImage.src = event.target.result;
                previewImage.classList.remove('hidden');
                imageUrl.value = '';
            };
            reader.readAsDataURL(file);
        }
    });

    imageUrl.addEventListener('change', (e) => {
        const url = e.target.value;
        if (url) {
            previewImage.src = url;
            previewImage.classList.remove('hidden');
            imageUpload.value = '';
        }
    });

 
    generateButton.addEventListener('click', async () => {
        let imageSource;
    
        if (imageUpload.files.length > 0) {
            imageSource = imageUpload.files[0];
        } else if (imageUrl.value) {
            imageSource = imageUrl.value;
        } else {
            alert('Please upload an image or provide an image URL');
            return;
        }

        captionResult.textContent = 'Generating caption...';
        captionResult.classList.remove('hidden');

        try {
            const payload = imageUpload.files.length > 0 
                ? { image_base64: previewImage.src }
                : { image_url: imageSource };

            const response = await fetch('/generate_caption', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success) {
                captionResult.textContent = data.caption;
            } else {
                captionResult.textContent = 'Error: ' + data.message;
            }
        } catch (error) {
            captionResult.textContent = 'Error generating caption: ' + error.message;
        }
    });
});
