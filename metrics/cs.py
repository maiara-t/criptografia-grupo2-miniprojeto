import os
import time


class CS:
    @staticmethod
    def calculate(compressed_path, compression_time_seconds):
        if not os.path.exists(compressed_path):
            raise FileNotFoundError("Compressed file path must exist.")

        if compression_time_seconds <= 0:
            raise ValueError("Compression time must be greater than zero.")

        compressed_size = os.path.getsize(compressed_path)
        speed = compressed_size / compression_time_seconds
        return speed
