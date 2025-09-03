# core/encryption.py

from cryptography.fernet import Fernet
from core.config import settings

# Initialize the encryption suite with your key from the settings
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_message(message: str) -> str:
    """Encrypts a plaintext message and returns the encrypted string."""
    encrypted_text = cipher_suite.encrypt(message.encode())
    return encrypted_text.decode()

def decrypt_message(encrypted_message: str) -> str:
    """Decrypts a message and returns the original plaintext."""
    try:
        decrypted_text = cipher_suite.decrypt(encrypted_message.encode())
        return decrypted_text.decode()
    except Exception:
        # If decryption fails (e.g., invalid key or corrupted data),
        # return a safe, non-crashing string.
        return "[Message could not be decrypted]"

