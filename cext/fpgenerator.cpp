//
//
//#include "Python.h"

#include "fpgenerator.h"

const poly ZERO = 0;
const poly ONE = 0x8000000000000000LL;

FPGenerator::FPGenerator(poly polynomial, int degree) {
  this->degree = degree;
  this->polynomial = polynomial;

  poly powerTable[128];
  poly x_to_the_i = ONE;
  const poly x_to_the_degree_minus_one = (ONE >> (degree - 1));

  for (int i = 0; i < 128; i++) {
    // Invariants:
    //   x_to_the_i = mod(x^i, polynomial)
    //   forall 0 <= j < i, powerTable[i] = mod(x^i, polynomial)
    powerTable[i] = x_to_the_i;
    bool overflow = ((x_to_the_i & x_to_the_degree_minus_one) != 0);
    x_to_the_i >>= 1;
    if (overflow) {
      x_to_the_i ^= polynomial;
    }
  }
  this->empty = powerTable[64];

  for (int i = 0; i < 16; i++) {
    for (int j = 0; j < 256; j++) {
      poly v = ZERO;
      for (int k = 0; k < 8; k++) {
	if ((j & (1 << k)) != 0) {
	  v ^= powerTable[127 - i * 8 - k];
	}
      }
      byteModTable[i][j] = v;
    }
  }
}

poly
FPGenerator::fp(const char *buf, int start, int n) {
  return extend(empty, buf, start, n);
}

poly
FPGenerator::extend(poly f, const char *buf, int start, int n) {
  for (int i = 0; i < n; i++) {
    f = extend_byte(f, buf[start + i]);
  }
  return reduce(f);
}

poly FPGenerator::reduce(poly fp) {
  const int N = (8 - degree/8);
  poly local = (N == 8 ? 0 : fp & (-1L << 8 * N));
  poly temp = ZERO;
  for (int i = 0; i < N; i++) {
    temp ^= byteModTable[8 + i][((int)fp) & 0xff];
    fp >>= 8;
  }
  return local ^ temp;
}

poly FPGenerator::extend_byte(poly f, byte v) {
  f ^= (0xff & v);
  int i = (int)f;
  poly result = (f >> 8);
  result ^= byteModTable[7][i & 0xff];
  return result;
}
