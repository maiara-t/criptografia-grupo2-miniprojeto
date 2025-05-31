import os


class CR:
    @staticmethod
    def calculate(original_path, embedded_path):
        if not os.path.exists(original_path) or not os.path.exists(embedded_path):
            raise FileNotFoundError("Both original and embedded image paths must exist.")

        original_size = os.path.getsize(original_path)
        embedded_size = os.path.getsize(embedded_path)

        if original_size == 0:
            raise ValueError("Original image size is zero, cannot calculate compression rate.")

        compression_rate = original_size / embedded_size
        return compression_rate
