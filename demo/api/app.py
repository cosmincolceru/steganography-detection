from flask import Flask, request, jsonify
import tensorflow as tf

app = Flask(__name__)

def process_image_for_inference(image_bytes, image_format):
    if image_format == 'image/png':
        img = tf.image.decode_png(image_bytes, channels=3)
    elif image_format == 'image/bmp':
        img = tf.image.decode_bmp(image_bytes, channels=3)
    elif image_format == 'image/jpeg':
        img = tf.image.decode_jpeg(image_bytes, channels=3)
    else:
        raise ValueError('Unsupported image format')

    img = tf.cast(img, tf.float32)
    img = img * (1.0 / 255.0)
    img = tf.expand_dims(img, axis=0)
    return img

# Load the model
model = tf.keras.models.load_model('20240607_srnet_lsb+jsteg_js+url-ft_45epoci.keras')

@app.route('/predict', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if image.content_type is None:
        if image.filename.lower().endswith('.png'):
            image_format = 'image/png'
        elif image.filename.lower().endswith('.bmp'):
            image_format = 'image/bmp'
        elif image.filename.lower().endswith('.jpeg') or image.filename.lower().endswith('.jpg'):
            image_format = 'image/jpeg'
        else:
            return jsonify({'error': 'Unsupported image format'}), 400
    else:
        image_format = image.content_type

    print(f"image_format: {image_format}")

    if image_format not in ['image/png', 'image/bmp', 'image/jpeg']:
        return jsonify({'error': 'Unsupported image format'}), 400

    # Read the image bytes
    image_bytes = image.read()

    # Check the image with the model
    try:
        image = process_image_for_inference(image_bytes, image_format)
        prediction = model.predict(image)
        return jsonify({'prediction': prediction.tolist()})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
