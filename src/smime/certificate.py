# Create and save certificates
# Run this script to do for Alice, Bob, and the AC.
import datetime
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.x509.oid import NameOID

from keygen import load_key


def create_certificate(
    key: RSAPrivateKey, subject: x509.Name, issuer: x509.Name
) -> x509.Certificate:
    """Creates a certificate from an RSA private key."""
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(
            # Our certificate will be valid for 10 days
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=10)
        )
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
            # Sign our certificate with our private key
        )
        .sign(key, hashes.SHA256())
    )
    return cert


def save_certificate(cert: x509.Certificate, savepath: str = "./certifiactes/cert.pem"):
    """Write our certificate out to disk."""

    with open(savepath, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


if __name__ == "__main__":

    # Various details about who we are. For a self-signed certificate the
    # subject and issuer are always the same.
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "FR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "IDF"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Paris"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Mines Paris"),
            x509.NameAttribute(NameOID.COMMON_NAME, "mines.org"),
        ]
    )

    if not Path("./keys").is_dir():
        # Run the keygen script to generate the keys
        exec(open("./src/smime/keygen.py").read())

    if not Path("./certificates").is_dir():
        Path("./certificates").mkdir()

    key = load_key(savepath="./keys/sk_alice.pem")
    certificate = create_certificate(key=key, subject=subject, issuer=issuer)
    save_certificate(cert=certificate, savepath="./certificates/cert_alice.pem")

    key = load_key(savepath="./keys/sk_bob.pem")
    certificate = create_certificate(key=key, subject=subject, issuer=issuer)
    save_certificate(cert=certificate, savepath="./certificates/cert_bob.pem")

    key = load_key(savepath="./keys/sk_ac.pem")
    certificate = create_certificate(key=key, subject=subject, issuer=issuer)
    save_certificate(cert=certificate, savepath="./certificates/cert_ac.pem")
