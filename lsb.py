import numpy as np
from PIL import Image

class LSB:
    def __init__(self, image, message=None):
        self.image = image
        self.message = message

    def apply(self):
        img_array = np.array(self.image)
        h, w, _ = img_array.shape

        binary_message = ''.join(format(ord(char), '08b') for char in self.message + '\0')
        total_bits = len(binary_message)

        idx = 0
        for i in range(h):
            for j in range(w):
                for k in range(3):
                    if idx >= total_bits:
                        break
                    img_array[i, j, k] = (img_array[i, j, k] & 254) | int(binary_message[idx])
                    idx += 1
                if idx >= total_bits:
                    break
            if idx >= total_bits:
                break

        return Image.fromarray(img_array)

    def extract(self):
        img_array = np.array(self.image)
        h, w, _ = img_array.shape

        bits = []
        for i in range(h):
            for j in range(w):
                for k in range(3):
                    bits.append(str(img_array[i, j, k] & 1))

        bytes_list = [''.join(bits[i:i + 8]) for i in range(0, len(bits), 8)]

        message = ""
        for byte in bytes_list:
            char = chr(int(byte, 2))
            if char == '\0':
                break
            message += char

        return message
