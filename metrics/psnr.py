import math


class PSNR:
    @staticmethod
    def calculate(mse, max_pixel_value=255):
        if mse <= 0:
            raise ValueError("MSE must be greater than 0 to calculate PSNR.")

        max_squared = max_pixel_value ** 2
        psnr = 10 * math.log10(max_squared / mse)
        return psnr
