import os
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np


class SSIM:
    @staticmethod
    def calculate(image_path1, image_path2):
        if not os.path.exists(image_path1) or not os.path.exists(image_path2):
            raise FileNotFoundError("Both image paths must exist.")

        image1 = Image.open(image_path1).convert("L")
        image2 = Image.open(image_path2).convert("L")

        img1_array = np.array(image1)
        img2_array = np.array(image2)

        if img1_array.shape != img2_array.shape:
            raise ValueError("Images must have the same dimensions for SSIM.")

        score, _ = ssim(img1_array, img2_array, full=True)
        return score
