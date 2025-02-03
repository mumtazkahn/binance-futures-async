import os
from typing import (
    Tuple,
    Union,
)

from cryptography.hazmat.primitives.asymmetric import (
    ed25519,
    rsa,
)
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from .ed25519 import Ed25519Auth
from .hmac import HMACAuth
from .rsa import RSAAuth


def detect_key_type(private_key: str) -> str:
    """
    Detect the type of cryptographic key based on the provided private key.
    """
    if os.path.isfile(private_key):
        with open(private_key, "rb") as f:
            private_key_data = f.read()
        try:
            key = load_pem_private_key(private_key_data, password=None)
            if isinstance(key, rsa.RSAPrivateKey):
                return "RSA"
            elif isinstance(key, ed25519.Ed25519PrivateKey):
                return "Ed25519"
        except ValueError:
            pass

    # If it's not a file or not RSA/Ed25519, assume it's HMAC
    return "HMAC"


def create_auth(
    api_key: str, private_key: str
) -> Tuple[Union[Ed25519Auth, RSAAuth, HMACAuth], str]:
    """
    Create and return the appropriate authentication object based on the key type,
    along with the detected key type.
    """
    key_type = detect_key_type(private_key)

    if key_type == "Ed25519":
        return Ed25519Auth(api_key, private_key), key_type
    elif key_type == "RSA":
        return RSAAuth(api_key, private_key), key_type
    else:  # HMAC
        return HMACAuth(api_key, private_key), key_type


# import os
# from typing import Union,Tuple
# from .ed25519 import Ed25519Auth
# from .rsa import RSAAuth
# from .hmac import HMACAuth

# def detect_key_type(private_key_path: str) -> str:
#     """
#     Detect the type of cryptographic key based on the provided private key file.
#     """
#     if not os.path.exists(private_key_path):
#         raise FileNotFoundError("Private key file is missing")

#     with open(private_key_path, 'rb') as f:
#         private_key_data = f.read()

#     try:
#         from cryptography.hazmat.primitives.serialization import load_pem_private_key
#         from cryptography.hazmat.primitives.asymmetric import rsa, ed25519

#         private_key = load_pem_private_key(private_key_data, password=None)

#         if isinstance(private_key, rsa.RSAPrivateKey):
#             return "RSA"
#         elif isinstance(private_key, ed25519.Ed25519PrivateKey):
#             return "Ed25519"
#     except:
#         # If loading fails, it's likely HMAC
#         return "HMAC"

#     raise ValueError("Unable to determine key type")

# def create_auth(api_key: str, private_key_path: str) -> Tuple[Union[Ed25519Auth, RSAAuth, HMACAuth], str]:
#     """
#     Create and return the appropriate authentication object based on the key type,
#     along with the detected key type.
#     """
#     key_type = detect_key_type(private_key_path)

#     if key_type == "Ed25519":
#         return Ed25519Auth(api_key, private_key_path), key_type
#     elif key_type == "RSA":
#         return RSAAuth(api_key, private_key_path), key_type
#     elif key_type == "HMAC":
#         with open(private_key_path, 'r') as f:
#             secret_key = f.read().strip()
#         return HMACAuth(api_key, secret_key), key_type
#     else:
#         raise ValueError(f"Unsupported key type: {key_type}")
