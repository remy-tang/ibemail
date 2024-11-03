# Weil Pairing Implementation
from sage.all import EllipticCurve, Integer
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.rings.finite_rings.finite_field_pari_ffelt import \
    FiniteFieldElement_pari_ffelt
from sage.rings.finite_rings.finite_field_prime_modn import \
    FiniteField_prime_modn
from sage.rings.infinity import PlusInfinity
from sage.schemes.elliptic_curves.ell_finite_field import \
    EllipticCurve_finite_field
from sage.schemes.elliptic_curves.ell_point import \
    EllipticCurvePoint_finite_field


def g(
    P: EllipticCurvePoint_finite_field,
    Q: EllipticCurvePoint_finite_field,
    x: Integer,
    y: Integer,
    E: EllipticCurve_finite_field,
) -> FiniteFieldElement_pari_ffelt:
    """First step of Miller's Algorithm.

    This defines a rational function g(x,y) on E whose divisor is div(g) = [P] + [Q] - [P+Q] - [O]
    (cf. Theorem 2.2).
    """
    A = E.a_invariants()[3]
    if P == E(0) or Q == E(0):
        return "no divisor"
    xP, yP = P[0], P[1]
    xQ, yQ = Q[0], Q[1]
    # Calculate slope of line connecting P and Q
    # JUST check if equal
    if yP == -yQ and xP == xQ:
        slope = PlusInfinity()
    elif P == Q:
        slope = (3 * (xP**2) + A) / (2 * yP)
    else:
        slope = (yQ - yP) / (xQ - xP)
    # return the function on E
    if slope == PlusInfinity():
        return x - xP
    else:
        return (y - yP - slope * (x - xP)) / (x + xP + xQ - slope**2)


def miller_algorithm(
    P: EllipticCurvePoint_finite_field,
    m: Integer,
    x: Integer,
    y: Integer,
    E: EllipticCurve_finite_field,
):
    """Implementation of Miller's algorithm (Theorem 2.2)."""
    binary = m.digits(2)  # gives number in binary
    n = len(binary)  # trying to find what "n" is.
    T = P
    f = 1
    for i in range(
        n - 2, -1, -1
    ):  # Stop once i = -1, so last number is 0...range(start, stop, step)
        f = (f**2) * g(T, T, x, y, E)
        T *= 2  # T = 2T
        if binary[i] == 1:
            f = f * g(T, P, x, y, E)
            T += P
    return f  # This algorithm returns a value...


def modified_weil_pairing(
    P: EllipticCurvePoint_finite_field,
    Q: EllipticCurvePoint_finite_field,
    m: Integer,
    E: EllipticCurve_finite_field,
    p: Integer,
) -> FiniteFieldElement_pari_ffelt:
    """
    Implementation of Modified Weil Pairing (cf. Definition 2.8)
    Works on the elliptic curve E given by y^2 = x^3 + 1 over F_p with p a prime congruent to 2 modulo 3
    """
    Fp: FiniteField_prime_modn = GF(p)
    R = Fp["x"]
    (x,) = R._first_ngens(1)
    Fp2 = Fp.extension(x ** Integer(2) + x + Integer(1), names=("z",))
    (z,) = Fp2._first_ngens(1)

    E_zeta = EllipticCurve(Fp2, [0, 1])
    # Define E: y^2 = x^3 + 1 over this field
    phiQ = E_zeta([z * Q[0], Q[1]])
    A = E_zeta.a_invariants()[3]
    P_zeta = E_zeta([P[0], P[1]])
    S = E_zeta.random_element()
    while m * S == E(0):
        S = E_zeta.random_element()
    xS, yS = S[0], S[1]
    QplusS = phiQ + S
    f_P_QplusS = miller_algorithm(P, m, QplusS[0], QplusS[1], E_zeta)
    f_P_S = miller_algorithm(P, m, xS, yS, E_zeta)
    num = f_P_QplusS / f_P_S

    PminusS = P_zeta - S  # modify
    f_Q_PminusS = miller_algorithm(
        phiQ, m, PminusS[0], PminusS[1], E_zeta
    )  # This is f_Q(P-S)
    f_Q_minusS = miller_algorithm(phiQ, m, xS, -yS, E_zeta)  # This is f_Q(-S)
    denom = f_Q_PminusS / f_Q_minusS

    e_m = num / denom
    return e_m
