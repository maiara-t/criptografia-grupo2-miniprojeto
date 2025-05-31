import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64


class AESHandler:
    def __init__(self, keys_directory, key_size):
        self.keys_directory = keys_directory
        self.key_size = key_size
        self.key_path = os.path.join(self.keys_directory, 'private.key')

    def generate_key(self):
        if not os.path.exists(self.keys_directory):
            os.makedirs(self.keys_directory)

        key = get_random_bytes(self.key_size)

        with open(self.key_path, 'wb') as f:
            f.write(key)

        print(f"AES key generated and saved at {self.key_path}")

    @staticmethod
    def load_key(key_path):
        with open(key_path, 'rb') as f:
            return f.read()

    @staticmethod
    def pad(data):
        pad_len = 16 - (len(data) % 16)
        return data + bytes([pad_len] * pad_len)

    @staticmethod
    def unpad(data):
        return data[:-data[-1]]

    @staticmethod
    def encrypt(data, key):
        if isinstance(data, str):
            data = data.encode('utf-8')

        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = AESHandler.pad(data)
        ciphertext = cipher.encrypt(padded_data)
        return base64.b64encode(iv + ciphertext).decode('utf-8')

    @staticmethod
    def decrypt(encrypted_data, key):
        raw = base64.b64decode(encrypted_data)
        iv = raw[:16]
        ciphertext = raw[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(ciphertext)
        return AESHandler.unpad(decrypted_data).decode('utf-8')
