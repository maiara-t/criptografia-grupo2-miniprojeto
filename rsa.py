import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class RSAHandler:
    def __init__(self, keys_directory, key_size):
        self.keys_directory = keys_directory
        self.key_size = key_size
        self.private_key_path = os.path.join(self.keys_directory, 'private.key')
        self.public_key_path = os.path.join(self.keys_directory, 'public.key')

    def generate_keys(self):
        if not os.path.exists(self.keys_directory):
            os.makedirs(self.keys_directory)

        key = RSA.generate(self.key_size)

        with open(self.private_key_path, 'wb') as private_file:
            private_file.write(key.export_key())

        with open(self.public_key_path, 'wb') as public_file:
            public_file.write(key.publickey().export_key())

        print(f"RSA keys generated and saved at {self.keys_directory}")

    @staticmethod
    def load_key(key_path):
        with open(key_path, 'rb') as f:
            key = RSA.import_key(f.read())
        return key

    @staticmethod
    def encrypt(data, public_key):
        cipher = PKCS1_OAEP.new(public_key)

        if isinstance(data, str):
            data = data.encode('utf-8')

        return cipher.encrypt(data)

    @staticmethod
    def decrypt(encrypted_data, private_key):
        cipher = PKCS1_OAEP.new(private_key)

        return cipher.decrypt(encrypted_data)
