import pywt
import numpy as np
from PIL import Image, PngImagePlugin
import os


class DWT:
    def __init__(self, wavelet='haar', quantization_step=25):
        self.wavelet = wavelet
        self.q_step = quantization_step

    def compress_image(self, image_path, message_image_path=None, output_path=None, level=1):
        img = Image.open(image_path).convert('YCbCr')
        y, cb, cr = [np.array(c) for c in img.split()]

        message_bits = None
        if message_image_path:
            message_img = Image.open(message_image_path).convert('L')
            message_bits = np.array(message_img) // 255

        cb_comp = self._process_channel(cb, level, message_bits)
        cr_comp = self._process_channel(cr, level, message_bits)

        final_img_ycbcr = Image.merge('YCbCr', (
            Image.fromarray(y.astype(np.uint8)),
            Image.fromarray(cb_comp.astype(np.uint8)),
            Image.fromarray(cr_comp.astype(np.uint8))
        ))

        final_img_rgb = final_img_ycbcr.convert('RGB')

        if output_path is None:
            base, ext = os.path.splitext(image_path)
            output_path = base + '_compressed_embedded.png'

        pnginfo = PngImagePlugin.PngInfo()

        final_img_rgb.save(output_path, format='PNG', optimize=True, pnginfo=pnginfo)
        print(f"Compressed stego image saved at: {output_path}")

        return final_img_rgb

    def _process_channel(self, channel, level, message_bits=None):
        coeffs = pywt.wavedec2(channel, self.wavelet, level=level)
        cA, *details = coeffs

        target_level = -1
        cH, cV, cD = details[target_level]

        def quantize(band):
            return np.round(band / self.q_step) * self.q_step

        cH = quantize(cH)
        cV = quantize(cV)
        cD = quantize(cD)

        if message_bits is not None:
            def embed_lsb(band):
                flat_band = band.flatten()
                msg_resized = np.resize(message_bits, flat_band.shape)
                band_int = flat_band.astype(np.int32)
                band_emb = (band_int & ~1) | msg_resized.flatten()
                return band_emb.reshape(band.shape)

            cH = embed_lsb(cH)
            cV = embed_lsb(cV)
            cD = embed_lsb(cD)

        details[target_level] = (cH, cV, cD)

        coeffs_processed = [cA] + details
        rec_channel = pywt.waverec2(coeffs_processed, self.wavelet)
        rec_channel = np.clip(rec_channel, 0, 255)

        return rec_channel.astype(np.uint8)

    def extract_message_image(self, image_path, level=1):
        img = Image.open(image_path).convert('YCbCr')
        _, cb, cr = [np.array(c) for c in img.split()]

        def extract_from_channel(channel):
            coeffs = pywt.wavedec2(channel, self.wavelet, level=level)
            cA, *details = coeffs
            target_level = -1
            cH, cV, cD = details[target_level]

            def extract_lsb(band):
                band_int = band.astype(np.int32)
                return (band_int & 1).astype(np.uint8)

            bits_cH = extract_lsb(cH).flatten()
            bits_cV = extract_lsb(cV).flatten()
            bits_cD = extract_lsb(cD).flatten()

            combined_bits = np.concatenate([bits_cH, bits_cV, bits_cD])
            total_required = 128 * 128
            combined_bits = combined_bits[:total_required]

            message_image = combined_bits.reshape((128, 128)) * 255
            return Image.fromarray(message_image.astype(np.uint8), mode='L')

        return extract_from_channel(cb)
