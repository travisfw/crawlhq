#!/usr/bin/python
# this is a Python implementation of st.ata.util.FPGenerator in Java.
# 
class Array2:
    '''simplistic 2-dimensional array object'''
    def __init__(self, dim1, dim2):
        # TODO: use array
        self.dim1 = dim1
        self.dim2 = dim2
        self.data = [None] * (dim1 * dim2)
    def __setitem__(self, xy, v):
        if xy[0] < 0 or xy[0] >= self.dim1:
            raise IndexError, 'index1 out of range'
        if xy[1] < 0 or xy[1] >= self.dim2:
            raise IndexError, 'index2 out of range'
        self.data[xy[0] + self.dim1 * xy[1]] = v
    def __getitem__(self, xy):
        if xy[0] < 0 or xy[0] >= self.dim1:
            raise IndexError, 'index1 out of range'
        if xy[1] < 0 or xy[1] >= self.dim2:
            raise IndexError, 'index2 out of range'
        return self.data[xy[0] + self.dim1 * xy[1]]
        
class FPGenerator:
    zero = 0
    one = 0x8000000000000000
    def __init__(self, polynomial, degree):
        '''Create a fingerprint generator. The fingerprints generated
        willl have degree degree and will be generated by polynomial.
        Requires that polynomial is an irreducible polynomial of degree
        degree'''
        self.degree = degree
        self.polynomial = polynomial

        self.ByteModTable = Array2(16, 256)
        PowerTable = [0] * 128

        x_to_the_i = self.one
        x_to_the_degree_minus_one = (self.one >> (degree - 1))
        for i in range(128):
            # Invariants:
            # x_to_the_i = mod(x^i, polynomial)
            # forall 0 <= j < i, PowerTable[i] = mod(x^i, polynomial)
            PowerTable[i] = x_to_the_i
            overflow = ((x_to_the_i & x_to_the_degree_minus_one) != 0)
            x_to_the_i >>= 1
            if overflow:
                x_to_the_i ^= polynomial
        self.empty = PowerTable[64]
        for i in range(16):
            for j in range(256):
                # Invariant: forall 0 <= i' < i, forall 0 <= j' < j,
                #   ByteModTable[i'][j'] = mod(x^(degree+i)*(f(j'),polynomial)
                v = self.zero
                for k in range(8):
                    # Invariant:
                    #   v = mod(x^(degree+i) * (f(j & ((1<<k)-1)), polynomial)
                    if (j & (1 << k)) != 0:
                        v ^= PowerTable[127 - i*8 - k]
                self.ByteModTable[i, j] = v

    def fp(self, s):
        '''long fp(CharSequence s) in Java'''
        return self.extend(self.empty, s)

    def extend(self, f, s):
        '''long extend(long f, CharSequence s) in Java'''
        for c in s:
            v = ord(c)
            f = self.extend_char(f, v)
        return self.reduce(f)

    def extend_char(self, f, v):
        '''long extend_char(long f, int v) in Java'''
        f ^= (0xffff & v)
        i = f
        result = (f >> 16)
        result ^= self.ByteModTable[6, i & 0xff]
        i >>= 8
        result ^= self.ByteModTable[7, i & 0xff]
        return result

    def reduce(self, fp):
        '''long reduce(long fp) in Java'''
        N = (8 - self.degree / 8)
        if N == 8:
            local = 0
        else:
            local = fp & ((0xffffffffffffffff << 8*N) & 0xffffffffffffffff)
        temp = self.zero
        for i in range(N):
            temp ^= self.ByteModTable[8+i, fp & 0xff]
            fp >>= 8
        return local ^ temp

    def __call__(self, s):
        '''Python-only syntactic sugar'''
        return self.fp(s)

def make(polynomial, degree):
    '''static FPGenerator#make(long polynomial, int degree) in Java.
    caching of created FPGenerator in originla Java code is omitted.'''
    return FPGenerator(polynomial, degree)

std32 = make(0x9B6C9A2F80000000, 32)
std64 = make(0xD74307D3FD3382DB, 64)
