from skimage.io import imread
from sklearn.metrics import mean_squared_error
from PIL import Image
import numpy as np
import os

class MSE:
    def calculate(self, original_path, embedded_path):
        if not os.path.exists(original_path) or not os.path.exists(embedded_path):
            raise FileNotFoundError("Both original and embedded image paths must exist.")

        # Usa PIL para garantir mesmo modo e tamanho
        original = Image.open(original_path).convert("YCbCr")
        embedded = Image.open(embedded_path).convert("YCbCr")

        # Redimensiona se necessário
        if original.size != embedded.size:
            embedded = embedded.resize(original.size)

        original_array = np.array(original)
        embedded_array = np.array(embedded)

        original_flat = original_array.flatten()
        embedded_flat = embedded_array.flatten()

        mse = mean_squared_error(original_flat, embedded_flat)
        return mse
