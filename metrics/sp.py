import os


class SP:
    @staticmethod
    def calculate(original_path, compressed_path):
        if not os.path.exists(original_path) or not os.path.exists(compressed_path):
            raise FileNotFoundError("Both original and compressed image paths must exist.")

        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(compressed_path)

        if original_size == 0:
            raise ValueError("Original file size is zero, cannot calculate saving percentage.")

        saving = (original_size - compressed_size) / original_size * 100
        return saving
