# Create and save keys
# Run this script to do for Alice, Bob, and the AC.
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key


def create_key(public_exponent: int = 65537, key_size: int = 2048) -> rsa.RSAPrivateKey:
    """Generate our key."""
    key = rsa.generate_private_key(
        public_exponent=public_exponent,
        key_size=key_size,
    )

    return key


def save_key(
    key: rsa.RSAPrivateKey,
    savepath: str,
    passphrase: str | None = None,
):
    """Write our key to disk for safe keeping."""
    with open(savepath, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=(
                    serialization.NoEncryption()
                    if passphrase is None
                    else serialization.BestAvailableEncryption(bytes(passphrase))
                ),
            )
        )


def load_key(savepath: str, password: str | None = None) -> rsa.RSAPrivateKey:
    """Load a saved key."""
    with open(savepath, "rb") as pem_in:
        pemlines = pem_in.read()
    key = load_pem_private_key(pemlines, password)
    return key


if __name__ == "__main__":

    if not Path("./keys").is_dir():
        Path("./keys").mkdir()

    key = create_key()
    save_key(key, savepath="./keys/sk_ac.pem", passphrase=None)

    key = create_key()
    save_key(key, savepath="./keys/sk_alice.pem", passphrase=None)

    key = create_key()
    save_key(key, savepath="./keys/sk_bob.pem", passphrase=None)
