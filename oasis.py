from dataclasses import dataclass

P = 1019
INV2 = pow(2, P-2, P)

@dataclass(frozen=True)
class F2:
    u: int
    v: int
    def __post_init__(self):
        object.__setattr__(self, "u", self.u % P)
        object.__setattr__(self, "v", self.v % P)
    def __add__(self, o):
        return F2(self.u+o.u, self.v+o.v)
    def __sub__(self, o):
        return F2(self.u-o.u, self.v-o.v)
    def __neg__(self):
        return F2(-self.u, -self.v)
    def __mul__(self, o):
        return F2(self.u*o.u - self.v*o.v,
                  self.u*o.v + self.v*o.u)
    def __truediv__(self, o):
        return self * o.inv()
    def __pow__(self, e):
        r = F2(1,0); a = self
        while e:
            if e & 1: r = r*a
            a = a*a; e >>= 1
        return r
    def inv(self):
        n = (self.u*self.u + self.v*self.v) % P
        ni = pow(n, P-2, P)
        return F2(self.u*ni, -self.v*ni)
    def key(self):
        return self.u + P*self.v
    def __eq__(self, o):
        return self.u == o.u and self.v == o.v

def F(u,v=0): return F2(u,v)

def sqrt_fp(x):
    x %= P
    if x == 0: return 0
    r = pow(x, (P+1)//4, P)
    return r if (r*r) % P == x else None

def sqrt_f2(z):
    if z == F(0,0): return F(0,0)
    a,b = z.u, z.v
    N = (a*a + b*b) % P
    s = sqrt_fp(N)
    if s is None:
        raise ValueError("D is not a square in F_{p^2}")
    for ss in (s, (-s) % P):
        X = ((a + ss) * INV2) % P
        x = sqrt_fp(X)
        if x is not None:
            if x == 0:
                Y = ((ss - a) * INV2) % P
                y = sqrt_fp(Y)
                if y is not None and (2*x*y) % P == b and (x*x-y*y) % P == a:
                    return F(x,y)
            else:
                y = (b * pow((2*x) % P, P-2, P)) % P
                if (x*x-y*y) % P == a and (2*x*y) % P == b:
                    return F(x,y)
    raise ValueError("sqrt failed")

def step(A, bit):
    D = A*A - F(4,0)
    sD = sqrt_f2(D)
    rp = (-A + sD) * F(INV2,0)
    rm = (-A - sD) * F(INV2,0)
    r0, r1 = sorted([rp, rm], key=lambda z: z.key())
    r = r0 if bit == 0 else r1
    Araw = F(6,0) + F(4,0)*A*r
    c1, c2 = Araw, -Araw
    return c1 if c1.key() < c2.key() else c2

def jinv(A):
    A2 = A*A
    num = (A2 - F(3,0))**3
    den = A2 - F(4,0)
    return F(256,0)*num/den

def route_A(A0, bits):
    A = A0
    for b in bits:
        A = step(A, int(b))
    return A

def H(A0, bits):
    return jinv(route_A(A0, bits))

# ---------- small-campus data ----------
P = 1019
INV2 = pow(2, P-2, P)
A0 = F(977,297)
L = 12
jstar = F(797,921)

# The problem's checks
assert step(A0,0) == F(747,288)
assert jinv(F(747,288)) == F(98,85)
assert step(A0,1) == F(79,218)
assert jinv(F(79,218)) == F(138,0)
assert H(A0,"01") == F(967,249)
assert H(A0,"000000000000") == F(348,660)
assert H(A0,"111111111111") == F(34,0)
assert H(A0,"011010010110") == F(98,934)
assert H(A0,"101100111000") == F(119,0)

routes = []
for n in range(1<<L):
    bits = format(n, f"0{L}b")
    if H(A0,bits) == jstar:
        routes.append(bits)

print("k =", len(routes))
print("routes =", routes)