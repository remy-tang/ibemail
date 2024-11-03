# Implementation of the PKG in the IBE scheme.
from Crypto.Hash import SHA512
from sage.all import ZZ, EllipticCurve, Integer
from sage.arith.misc import is_prime, random_prime
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.schemes.elliptic_curves.ell_finite_field import \
    EllipticCurve_finite_field


class AbstractIBE:
    """
    Abstract class for IBE schemes.
    """

    def __init__(self):
        self.q: Integer  # A prime number
        self.p: Integer  # Another prime
        self.l: Integer  # An integer
        self.E: EllipticCurve_finite_field  # An elliptic curve over Fp
        self.P: Integer  # A point of order q
        self.P_pub: Integer  # The public key

    def hash_identity(self, identity: str) -> int:
        """Hash an identity string to an integer."""
        hash = SHA512.new()
        str_val = str(identity)
        byte_val = str_val.encode()
        hash.update(byte_val)
        hexadecimal = hash.hexdigest()
        return int(hexadecimal, 16)

    def __map_to_point(self, y0):
        """
        Map an integer `y0` to a point on the elliptic curve `E`.
        """
        x0 = pow(
            (y0 ** Integer(2)) - Integer(1),
            ((Integer(2) * self.p) - Integer(1)) // Integer(3),
            self.p,
        )  # `pow` is Python's built-in function that does fast power
        Q = self.E([x0, y0])
        return self.l * Q  # l comes from BDHGenerator. It's the integer s.t. p = lq-1

    def derive_public_key(self, user_identity: str):
        """
        Derive the public key for a user with identity `user_identity`.
        """
        y0 = self.hash_identity(user_identity)
        Q_ID = self.__map_to_point(y0)
        return Q_ID


class PKG(AbstractIBE):
    """
    Implementation of BDHGenerator
    This is `PKG` in IBE scheme ###2
    (cf. Algorithm 1 in Section 3.1)

    The PKG is responsible for:
    - Generating the public parameters for the scheme
    - Generating the private master key

    The PKG is run once and the public parameters are shared with all users.
    """

    def __init__(self):
        self.k: int  # Number of bits of the prime number q

        self.s: int  # The private master key in Z_q*.

    def __pick_k_bit_prime(self, prove_primality=True):
        """
        Generate a random k-bit prime `q`.

        If `prove_primality` is `False`, then pseudo-primality tests are used
        (not recommended).
        """
        self.q = random_prime(
            n=(Integer(2) ** self.k) - Integer(1),
            proof=prove_primality,
            lbound=Integer(2) ** (self.k - Integer(1)),
        )

    def __find_suitable_prime(self):
        """
        Given a prime `q`, find the smallest prime `p` such that:
        - `p % 3 == 2`
        - `(p + 1) % (q**2) != 0`

        Also finds the integer `l` such that `p` = `lq`-1.
        """
        p = self.q
        l = Integer(1)  # need l for `MapToPoint`
        lq = self.q
        while True:
            l += Integer(1)
            lq += self.q
            p = lq - Integer(1)
            # Find prime satisfying certain conditions
            if (
                p % Integer(3) == Integer(2)
                and (p + Integer(1)) % (self.q ** Integer(2)) != Integer(0)
                and is_prime(p)
            ):
                break

        self.p = p
        self.l = l

    def __generate_elliptic_curve(self):
        """Generate an elliptic curve over `Fp`."""
        self.E = EllipticCurve(GF(self.p), [Integer(0), Integer(1)])

    def __find_point_of_order_q(self):
        """Find a point `P` of order `q`."""
        P = self.E(Integer(Integer(0)))
        while P == self.E(Integer(0)):
            Q = self.E.random_element()
            while Q == self.E(Integer(0)):  # make sure P is not O
                Q = self.E.random_element()
            h = (self.p + Integer(1)) // self.q  # This is to make sure P has order q.
            P = h * Q  # Order of P is q1
        self.P = P

    def __select_random_secret(self):
        """
        The PKG selects a random secret `s` given the prime `q`.
        """
        self.s = ZZ.random_element(Integer(2), self.q - Integer(1))

    def __compute_public_key(self):
        """
        The PKG computes the public key as `P_pub` = `s` * `P`,
        where P is a fixed generator of G.
        """
        self.P_pub = self.s * self.P

    def setup(self, k: int):
        """
        Implementation of BDHGenerator
        This is `Setup` algorithm in IBE scheme ###2
        (cf. Algorithm 2 in Section 3.1)
        """
        self.k = k
        self.__pick_k_bit_prime()  # q
        self.__find_suitable_prime()  # p, l
        self.__generate_elliptic_curve()  # E
        self.__find_point_of_order_q()  # P
        self.__select_random_secret()  # s
        self.__compute_public_key()  # P_pub

    def get_public_params(self) -> dict:
        """Get the public parameters from the PKG."""
        if not (self.P_pub):
            raise AttributeError("Parameters not found. Run `setup` first.")
        return {
            "p": self.p,
            "q": self.q,
            "l": self.l,
            "E": self.E,
            "P": self.P,
            "P_pub": self.P_pub,
        }

    def generate_private_key(self, user_identity: str) -> int:
        """
        Generate a private key for a user with identity `user_identity`.
        """
        Q_ID = self.derive_public_key(user_identity)
        d_ID = self.s * Q_ID
        return d_ID
