# Implementation of the Boneh-Franklin IBE scheme.

from .pkg import PKG, AbstractIBE
from sage.all import ZZ
from .weil_pairing import modified_weil_pairing

def text_to_int(w):
    # ASCII implementation
    n = 0
    counter = 0
    # counter will give us the index of each character in the string
    for i in w:
        n = n + ord(i) * (256**counter)
        counter = counter + 1
    return n


def int_to_text(n):
    str = ""
    while n > 0:
        a0 = n % 256
        str = str + chr(
            a0
        )  # chr undoes ord. ord() inputs character and outputs integer. str inputs integer between 0 and 255 and outputs character.
        n = n // 256  # This is the quotient after dividing n by 256
    return str


class IBEClient(AbstractIBE):
    def __init__(self, email_address, public_params):
        self.email_address: str = email_address
        self.known_identities = {}
        self.d_ID: int
        self.set_params(public_params)

    def set_params(self, params: dict):
        """
        Set the public parameters for the IBE scheme.
        """
        self.p = params["p"]
        self.q = params["q"]
        self.l = params["l"]
        self.E = params["E"]
        self.P = params["P"]
        self.P_pub = params["P_pub"]

    def set_d_ID(self, d_ID):
        """Set the private key for the client."""
        self.d_ID = d_ID

    def __fast_power_small(self, g, A):
        """Fast modular exponentiation algorithm (needed for F_{p^2})."""
        if g == 0 and A == 0:
            return "Undefined"
        else:
            a = g
            b = 1
            while A > 0:
                if A % 2 == 1:
                    b = b * a
                a = a**2
                A = A // 2
            return b

    def __compute_pairing_secret(self, Q_ID):
        """Compute the pairing secret for the client."""
        r = ZZ.random_element(2, self.q - 1)
        U = r * self.P
        g_ID = modified_weil_pairing(Q_ID, self.P_pub, self.q, self.E, self.p)
        g_ID_to_r = self.__fast_power_small(g_ID, r)
        return U, g_ID_to_r

    def __encrypt_message(self, M, g_ID_to_r):
        """Encrypt a message M using the pairing secret g_ID_to_r."""
        return M.__xor__(self.hash_identity(g_ID_to_r))

    def __decrypt_cipher(self, V, weil):
        """Decrypt a cipher V using the Weil pairing."""
        return V.__xor__(self.hash_identity(weil))
    
    def encrypt_from_address(self, input_message, identity):
        """Encrypt a message for a user given their identity."""
        Q_ID = self.derive_public_key(identity)
        ciphertext = self.encrypt(input_message, Q_ID)
        return ciphertext

    def encrypt(self, m, Q_ID):
        """Encrypt a message m for a user with identity Q_ID."""
        M = text_to_int(m)
        U, g_ID_to_r = self.__compute_pairing_secret(Q_ID)
        V = self.__encrypt_message(M, g_ID_to_r)
        C = [U, V]  # This is the ciphertext
        return C

    def decrypt(self, C):
        """Decrypt a ciphertext C."""
        U, V = C
        weil = modified_weil_pairing(self.d_ID, U, self.q, self.E, self.p)
        M = self.__decrypt_cipher(V, weil)
        return int_to_text(M)


if __name__ == "__main__":
    # Create the PKG
    pkg = PKG()
    pkg.setup(512) # 512-bit security level
    public_params = pkg.get_public_params()

    # Create the clients and set their private key
    alice = IBEClient(email_address="alice@pesto.cyber", public_params=public_params)
    d_ID_alice = pkg.generate_private_key("alice@pesto.cyber")
    alice.set_d_ID(d_ID_alice)

    bob = IBEClient(email_address="bob@pesto.cyber", public_params=public_params)
    d_ID_bob = pkg.generate_private_key("bob@pesto.cyber")
    bob.set_d_ID(d_ID_bob)

    # Encrypt a message for Alice
    input_message = "Hello! :)"
    Q_ID = alice.derive_public_key("bob@pesto.cyber")
    ciphertext = alice.encrypt(input_message, Q_ID)

    print("Ciphertext:", ciphertext)

    # Decrypt the message
    output_message = bob.decrypt(ciphertext)
    print("Decrypted message:", output_message)
