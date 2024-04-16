# a simple script to demonstrate image augmentation

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import numpy as np

# Define the image data generator with augmentation options
datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest')

# Load a sample image for demonstration
image_path = 'sample_image.jpg'  # Change this to your image path
image = tf.keras.preprocessing.image.load_img(image_path)
x = tf.keras.preprocessing.image.img_to_array(image)
x = np.expand_dims(x, axis=0)

# Generate augmented images
i = 0
plt.figure(figsize=(12, 6))
for batch in datagen.flow(x, batch_size=1):
    plt.subplot(3, 4, i + 1)
    imgplot = plt.imshow(tf.keras.preprocessing.image.array_to_img(batch[0]))
    i += 1
    if i % 12 == 0:
        break

plt.show()
