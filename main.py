import os

from huffman import Huffman
from metrics.ct import CT
from metrics.cr import CR
from metrics.sp import SP
from metrics.cs import CS
from metrics.mse import MSE
from metrics.bpp import BPP
from metrics.ssim import SSIM
from metrics.psnr import PSNR
from rsa import RSAHandler
from aes import AESHandler
from dwt import DWT
from lsb import LSB
from PIL import Image
from Crypto.Random import get_random_bytes

import base64
import json

ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

RSA = RSAHandler(f"{ROOT_DIRECTORY}/keys/rsa", 2048)
AES = AESHandler(f"{ROOT_DIRECTORY}/keys/aes", 32)
HUFFMAN = Huffman()
DWT = DWT()

METRICS_FILE = f"{ROOT_DIRECTORY}/metrics-results.json"


def save_metrics(image, method, cr, ct, cs, sp, mse, ssim, bbp, psnr):
    new_metrics = {
        "image": image,
        "method": method,
        "cr": cr,
        "ct": ct,
        "cs": cs,
        "sp": sp,
        "mse": mse,
        "ssim": ssim,
        "bbp": bbp,
        "psnr": psnr
    }

    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(new_metrics)

    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def message_embedding_rsa(message):
    public_key = RSA.load_key(f"{ROOT_DIRECTORY}/keys/rsa/public.key")

    encrypted_message = RSA.encrypt(message, public_key)
    encoded_message = HUFFMAN.encode(encrypted_message)

    return base64.b64encode(encoded_message.encode()).decode()


def message_embedding_aes(message):
    private_key = AES.load_key(f"{ROOT_DIRECTORY}/keys/aes/private.key")

    encrypted_message = AES.encrypt(message, private_key)
    encoded_message = HUFFMAN.encode(encrypted_message)

    return base64.b64encode(encoded_message.encode()).decode()


def message_embedding_hybrid(message):
    aes_key = get_random_bytes(32)

    encrypted_message = AESHandler.encrypt(message, aes_key)

    public_key = RSA.load_key(f"{ROOT_DIRECTORY}/keys/rsa/public.key")
    encrypted_aes_key = RSA.encrypt(aes_key, public_key)

    encoded_message = HUFFMAN.encode(encrypted_message)

    combined = (
            base64.b64encode(encrypted_aes_key).decode('utf-8')
            + "|" +
            base64.b64encode(encoded_message.encode()).decode('utf-8')
    )

    return combined


def message_extracting_hybrid(message):
    encrypted_key_b64, encoded_message_b64 = message.split("|")

    encrypted_key = base64.b64decode(encrypted_key_b64)

    private_key = RSA.load_key(f"{ROOT_DIRECTORY}/keys/rsa/private.key")
    aes_key = RSA.decrypt(encrypted_key, private_key)

    decoded_message = base64.b64decode(encoded_message_b64).decode('utf-8')
    decrypted_compressed = HUFFMAN.decode(decoded_message)

    return AESHandler.decrypt(decrypted_compressed, aes_key)


def message_extracting_aes(message):
    base64_decoded = base64.b64decode(message.encode()).decode('utf-8')
    decoded_message = HUFFMAN.decode(base64_decoded)

    key = AES.load_key(f"{ROOT_DIRECTORY}/keys/aes/private.key")

    return AES.decrypt(decoded_message, key)


def message_extracting_rsa(message):
    base64_decoded = base64.b64decode(message.encode()).decode('utf-8')
    decoded_message = HUFFMAN.decode(base64_decoded)

    private_key = RSA.load_key(f"{ROOT_DIRECTORY}/keys/rsa/private.key")

    return RSA.decrypt(decoded_message, private_key).decode('utf-8')


def image_embedding(image_path, binary_image_path, output_path):
    compressed_image = DWT.compress_image(image_path, binary_image_path, output_path)
    return compressed_image


def paper_embedding_process(message, image_path, embedded_image_path, binary_image_path, compressed_image_path, method):
    ct = CT()
    cr = CR()
    cs = CS()
    sp = SP()
    mse = MSE()
    bpp = BPP()
    psnr = PSNR()
    ssim = SSIM()

    ct.start()

    if method == "rsa":
        compressed_encrypted_message = message_embedding_rsa(message)
    elif method == "aes":
        compressed_encrypted_message = message_embedding_aes(message)
    elif method == "hybrid":
        compressed_encrypted_message = message_embedding_hybrid(message)
    else:
        raise ValueError(f"Invalid cypher method: {method}")

    message_bytes = base64.b64decode(compressed_encrypted_message)
    binary_message = ''.join(format(byte, '08b') for byte in message_bytes)
    bin_to_image(binary_message, binary_image_path)

    compressed_image = image_embedding(image_path, binary_image_path, compressed_image_path)

    lsb = LSB(compressed_image, compressed_encrypted_message)
    embedded_image = lsb.apply()

    compressed_time = ct.stop()

    embedded_image.save(embedded_image_path, optimize=True)

    mse_value = mse.calculate(image_path, embedded_image_path)

    save_metrics(
        image=os.path.basename(image_path),
        method=method,
        cr=cr.calculate(image_path, embedded_image_path),
        ct=compressed_time,
        cs=cs.calculate(embedded_image_path, compressed_time),
        sp=sp.calculate(image_path, embedded_image_path),
        mse=mse_value,
        ssim=ssim.calculate(image_path, embedded_image_path),
        bbp=bpp.calculate(embedded_image_path),
        psnr=psnr.calculate(mse_value),
    )

    return embedded_image


def paper_extract_process(image, method):
    lsb = LSB(image)
    lsb_extracted_message = lsb.extract()

    if method == "rsa":
        return message_extracting_rsa(lsb_extracted_message)
    elif method == "aes":
        return message_extracting_aes(lsb_extracted_message)
    elif method == "hybrid":
        return message_extracting_hybrid(lsb_extracted_message)
    else:
        raise ValueError(f"Invalid cypher method: {method}")


def bin_to_image(binary_string, output_path):
    width, height = (128, 128)
    total_pixels = width * height

    binary_string = binary_string.ljust(total_pixels, '0')[:total_pixels]

    image = Image.new("1", (width, height))

    pixels = [int(bit) for bit in binary_string]
    image.putdata(pixels)

    image.save(output_path)

    return image


def main():
    images = ["lena.png", "apple.png", "bear.png", "man.png", "woman.png"]
    methods = ["rsa", "aes", "hybrid"]
    message = "Saudacoes Cordiais Vitinho"

    for method in methods:
        print(f"\n{'-' * 50}")
        print(f"\nCypher method: {method.upper()}")
        for image_name in images:
            image_path = os.path.join(ROOT_DIRECTORY, "images", image_name)

            base_name_lsb = image_name.replace(".png", f"_{method}_lsb.png")
            base_name_binary = image_name.replace(".png", f"_{method}_binary.png")
            base_name_compressed = image_name.replace(".png", f"_{method}_compressed.png")
            embedded_image_path = os.path.join(ROOT_DIRECTORY, "images", base_name_lsb)
            binary_image_path = os.path.join(ROOT_DIRECTORY, "images", base_name_binary)
            compressed_image_path = os.path.join(ROOT_DIRECTORY, "images", base_name_compressed)

            print(f"\nProcessing image [{image_name}] with {method.upper()} cypher method")

            paper_embedding_process(message, image_path, embedded_image_path, binary_image_path, compressed_image_path,
                                    method)

            image_to_extract = Image.open(embedded_image_path)

            extracted_image = DWT.extract_message_image(embedded_image_path)
            extracted_image.show()

            extracted_message = paper_extract_process(image_to_extract, method)

            print(f'Original image entropy: {Image.open(image_path).entropy():5f}')
            print(f'Estego image entropy: {Image.open(embedded_image_path).entropy():5f}')

            print(f"Message extracted: {extracted_message}")


if __name__ == "__main__":
    main()
