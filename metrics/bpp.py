import os
from PIL import Image


class BPP:
    @staticmethod
    def calculate(image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError("Compressed image path must exist.")

        compressed_size_bytes = os.path.getsize(image_path)
        compressed_bits = compressed_size_bytes * 8

        with Image.open(image_path) as img:
            width, height = img.size
            total_pixels = width * height

        if total_pixels == 0:
            raise ValueError("Image has no pixels (width or height is zero).")

        bpp = compressed_bits / total_pixels
        return bpp
