import string
import random
from PIL import Image


# =========================
# Substitution Cipher Setup
# =========================
def get_cipher_map():
    """
    Creates a substitution cipher map for:
    - Lowercase letters (a-z)
    - Uppercase letters (A-Z)
    - Digits (0-9)
    - Space ' '

    Each character is mapped to a unique 3-character code.
    """
    characters = string.ascii_letters + string.digits   # a-z, A-Z, 0-9
    cipher_map = {}
    used_codes = set()

    def generate_code():
        """Generate a unique random 3-character code (letters + digits)"""
        while True:
            code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))
            if code not in used_codes:
                used_codes.add(code)
                return code

    # Assign unique codes to all characters
    for ch in characters:
        cipher_map[ch] = generate_code()

    # Add space with a fixed marker
    cipher_map[' '] = '$$$'

    # Create reverse map for decryption
    reverse_map = {v: k for k, v in cipher_map.items()}

    return cipher_map, reverse_map


# Create the maps
ENCRYPT_MAP, DECRYPT_MAP = get_cipher_map()
CODE_LENGTH = 3


def encrypt(text):
    return "".join(ENCRYPT_MAP.get(char, char) for char in text)


def decrypt(text):
    decrypted_text, i = [], 0
    while i < len(text):
        codeword = text[i:i + CODE_LENGTH]
        if codeword in DECRYPT_MAP:
            decrypted_text.append(DECRYPT_MAP[codeword])
            i += CODE_LENGTH
        else:
            decrypted_text.append(text[i])
            i += 1
    return "".join(decrypted_text)


# =========================
# Steganography Functions
# =========================
def message_to_binary(message):
    """Convert string to binary"""
    return ''.join(format(ord(ch), '08b') for ch in message)


def binary_to_message(binary_str):
    """Convert binary back to string"""
    chars = [binary_str[i:i + 8] for i in range(0, len(binary_str), 8)]
    return ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)


def encode_image(input_image_path, output_image_path, secret_message, region=None):
    """
    Hide secret_message in the image using LSB.
    region = (x_start, y_start, x_end, y_end) to limit embedding area.
    """
    img = Image.open(input_image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    binary_msg = message_to_binary(secret_message) + "1111111111111110"  # End marker
    data_index = 0

    pixels = img.load()
    width, height = img.size

    x0, y0, x1, y1 = region if region else (0, 0, width, height)

    for y in range(y0, y1):
        for x in range(x0, x1):
            if data_index >= len(binary_msg):
                break

            r, g, b = pixels[x, y]

            # Modify the LSB of red, green, blue channels
            r = (r & ~1) | int(binary_msg[data_index])
            data_index += 1
            if data_index < len(binary_msg):
                g = (g & ~1) | int(binary_msg[data_index])
                data_index += 1
            if data_index < len(binary_msg):
                b = (b & ~1) | int(binary_msg[data_index])
                data_index += 1

            pixels[x, y] = (r, g, b)

        if data_index >= len(binary_msg):
            break

    img.save(output_image_path)
    print(f"✅ Message hidden inside {output_image_path}")


def decode_image(stego_image_path, region=None):
    """Extract hidden message from image"""
    img = Image.open(stego_image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    pixels = img.load()
    width, height = img.size

    x0, y0, x1, y1 = region if region else (0, 0, width, height)

    binary_msg = ""
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = pixels[x, y]
            binary_msg += str(r & 1)
            binary_msg += str(g & 1)
            binary_msg += str(b & 1)

    # Stop at marker
    end_marker = "1111111111111110"
    end_index = binary_msg.find(end_marker)
    if end_index != -1:
        binary_msg = binary_msg[:end_index]

    return binary_to_message(binary_msg)


# =========================
# Main Program
# =========================
def main():
    print("--- Simple Code Word Encryptor/Decryptor with Steganography ---")

    while True:
        print("\nChoose an operation:")
        print("1. Encrypt text (Encode)")
        print("2. Decrypt text (Decode)")
        print("3. Hide Encrypted Text in Image")
        print("4. Extract and Decrypt from Image")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            sentence = input("Enter the sentence to ENCRYPT: ")
            encrypted_output = encrypt(sentence)
            print("\n✅ Original Sentence: ", sentence)
            print("🔐 Encrypted Codeword:", encrypted_output)

        elif choice == '2':
            codeword = input("Enter the codeword to DECRYPT: ")
            decrypted_output = decrypt(codeword)
            print("\n🔐 Codeword:", codeword)
            print("✅ Decrypted Sentence:", decrypted_output)

        elif choice == '3':
            sentence = input("Enter the sentence to ENCRYPT & HIDE: ")
            encrypted_output = encrypt(sentence)
            input_image = input("Enter input image path: ")
            output_image = input("Enter output image path: ")
            encode_image(input_image, output_image, encrypted_output)

        elif choice == '4':
            stego_image = input("Enter stego image path: ")
            hidden_message = decode_image(stego_image)
            decrypted_output = decrypt(hidden_message)
            print("\n🔎 Extracted Encrypted Codeword:", hidden_message)
            print("✅ Decrypted Sentence:", decrypted_output)

        elif choice == '5':
            print("Exiting the program. Goodbye! 👋")
            break

        else:
            print("❌ Invalid choice. Please enter 1–5.")


if __name__ == "__main__":
    main()