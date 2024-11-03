from M2Crypto import BIO, SMIME, X509


def create_smime(
    from_addr: str,
    to_addrs: str,
    subject: str,
    msg: bytes,
    from_key: str,
    from_cert: str | None = None,
    to_certs: list[str] | None = None,
) -> str:
    """Create an S/MIME message."""

    msg_bio = BIO.MemoryBuffer(msg)
    sign = from_key
    encrypt = to_certs

    s = SMIME.SMIME()
    if sign:
        s.load_key(from_key, from_cert)
        if encrypt:
            p7 = s.sign(msg_bio, flags=SMIME.PKCS7_TEXT)
        else:
            p7 = s.sign(msg_bio, flags=SMIME.PKCS7_TEXT | SMIME.PKCS7_DETACHED)
        msg_bio = BIO.MemoryBuffer(msg)  # Recreate coz sign() has consumed it.

    if encrypt:
        sk = X509.X509_Stack()
        for x in to_certs:
            sk.push(X509.load_cert(x))
        s.set_x509_stack(sk)
        s.set_cipher(SMIME.Cipher("des_ede3_cbc"))
        tmp_bio = BIO.MemoryBuffer()
        if sign:
            s.write(tmp_bio, p7)
        else:
            tmp_bio.write(msg)
        p7 = s.encrypt(tmp_bio)

    out = BIO.MemoryBuffer()
    out.write(f"From: {from_addr}\r\n")
    out.write(
        f"To: {to_addrs.join(", ") if isinstance(to_addrs, list) else to_addrs}\r\n"
    )
    out.write(f"Subject: {subject}\r\n")
    # out.write("From: %s\r\n" % from_addr)
    # out.write("To: %s\r\n" % str.join(to_addrs, ", "))
    # out.write("Subject: %s\r\n" % subject)
    if encrypt:
        s.write(out, p7)
    else:
        if sign:
            s.write(out, p7, msg_bio, SMIME.PKCS7_TEXT)
        else:
            out.write("\r\n")
            out.write(msg)
    out.close()

    return out.read().decode()


if __name__ == "__main__":
    create_smime(
        from_addr="alice@pesto.ibe",
        to_addrs="bob@pesto.ibe",
        subject="test",
        msg=b"test",
        from_key="./keys/sk_alice.pem",
        from_cert="./certificates/cert_alice.pem",
        to_certs=["./certificates/cert_bob.pem"],
    )
