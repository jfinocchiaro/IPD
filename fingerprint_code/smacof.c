/* Copyright (C) 2014 Jeffrey Tsang
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
 *
 * Return codes of this program
 * -1: no runtime argument for run number
 *  0: success
 *  1: malloc() failure
 *  2: fopen() failure
 *  3: fread() failure
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#define SIZE   2048				/* Total count of all clusters in the dataset */
#define POINT  500				/* Number of distinct clusters in the dataset */
#define DIMS   10				/* Number of Euclidean dimensions to embed into */
#define RDISTF "D3LT-80r"		/* Filename of the reduced distance matrix */
#define RLISTF "D3LTr.list"		/* Filename of the cluster list */
#define FNAME1 "D3LT-%dmds%d"	/* Filename of the MDS summary data, printf format with two ints */
#define FNAME2 "D3LT-%dmds%db"	/* Filename of the best MDS configuration, printf format with two ints */
#define FNAME3 "D3LT-%dmds%dr"	/* Filename of the MDS temporary saved configuration, printf format with two ints */

/* Copyright (C) 1997 - 2002, Makoto Matsumoto and Takuji Nishimura, All rights reserved.                          
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * 3. The names of its contributors may not be used to endorse or promote products derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Any feedback is very welcome. http://www.math.keio.ac.jp/matumoto/emt.html email: matumoto@math.keio.ac.jp
 */
static unsigned long mt[624];
static int mti = 625;

void srandMT(unsigned long s) {
    mt[0] = (s | 1U) & 0xFFFFFFFFUL;
    for (mti = 1; mti < 624; mti++) {
        mt[mti] = (1812433253UL * (mt[mti - 1] ^ (mt[mti - 1] >> 30)) + mti);
        mt[mti] &= 0xFFFFFFFFUL;
    }
}

unsigned long randMT() {
    unsigned long y;
    static unsigned long mag01[2] = {0x0UL, 0x9908B0DFUL};
    if (mti >= 624) {
        int k;
        for (k = 0; k < 227; k++) {
            y = (mt[k] & 0x80000000UL) | (mt[k + 1] & 0x7FFFFFFFUL);
            mt[k] = mt[k + 397] ^ (y >> 1) ^ mag01[y & 0x1UL];
        }
        for (; k < 623; k++) {
            y = (mt[k] & 0x80000000UL) | (mt[k + 1] & 0x7FFFFFFFUL);
            mt[k] = mt[k - 227] ^ (y >> 1) ^ mag01[y & 0x1UL];
        }
        y = (mt[623] & 0x80000000UL) | (mt[0] & 0x7FFFFFFFUL);
        mt[623] = mt[396] ^ (y >> 1) ^ mag01[y & 0x1UL];
        mti = 0;
    }
    y = mt[mti++];
    y ^= (y >> 11);
    y ^= (y << 7) & 0x9D2C5680UL;
    y ^= (y << 15) & 0xEFC60000UL;
    y ^= (y >> 18);
    return y;
}
/* end MT19937 code */

#if !defined(__STDC_VERSION__) || (__STDC_VERSION__ < 199901L)
#define restrict
#endif
double err = 1e20;
long tot = (long)SIZE * SIZE;
char alive = 1;

void handler(int sig) {
	alive = 0;
}

inline void* trymalloc(size_t size) {
	int c1;
	void* ret;
	for (c1 = 0; c1 < 10; c1++) {
		if (ret = malloc(size)) {
			return ret;
		}
		sleep(5);
	}
	fprintf(stderr, "MALLOC FAIL!\n");
	exit(1);
}

inline FILE* tryfopen(const char* name, const char* mode) {
	int c1;
	FILE* ret;
	for (c1 = 0; c1 < 10; c1++) {
		if (ret = fopen(name, mode)) {
			return ret;
		}
		sleep(5);
	}
	fprintf(stderr, "FOPEN %s FAIL!\n", name);
	exit(2);
}

inline void seterr(double val) {
	if (val > 1e-5 && val < err) {
		err = val;
	}
}

void iterate(const double* restrict D, const double* restrict v, const double* restrict u, const double* restrict w, double* restrict x, int ct, const char* name, const char* name2, const char* name3, int* gct, int* tct) {
	int c1, c2, c3, c4;
	double b[POINT], t[DIMS * POINT], y[DIMS * POINT], d1, d2, eps = 0, cer = 0;
	FILE* file;
	do {
		memset(b, 0, sizeof(double) * POINT);
		memset(t, 0, sizeof(double) * DIMS * POINT);
		for (c1 = 0, c4 = 0; c1 < POINT - 1; c1++) {
			for (c2 = c1 + 1; c2 < POINT; c2++) {
				for (d1 = 0, c3 = 0; c3 < DIMS; c3++) {
					d1 += pow(x[c1 * DIMS + c3] - x[c2 * DIMS + c3], 2);
				}
				if (d1 > 1e-20) { /* Tolerance for nonzero norm */
					d1 = w[c1] * w[c2] * D[c4] / sqrt(d1);
					for (c3 = 0; c3 < DIMS; c3++) {
						t[c1 * DIMS + c3] -= d1 * x[c2 * DIMS + c3];
					}
					for (c3 = 0; c3 < DIMS; c3++) {
						t[c2 * DIMS + c3] -= d1 * x[c1 * DIMS + c3];
					}
					b[c1] += d1;
					b[c2] += d1;
				}
				c4++;
			}
		}
		for (c1 = 0; c1 < POINT; c1++) {
			for (c3 = 0; c3 < DIMS; c3++) {
				t[c1 * DIMS + c3] += b[c1] * x[c1 * DIMS + c3];
			}
		}
		for (c3 = 0; c3 < DIMS; c3++) {
			for (d1 = 0, d2 = 0, c2 = 0; c2 < POINT; c2++) {
				d1 += t[c2 * DIMS + c3];
				d2 += t[c2 * DIMS + c3] * v[c2];
			}
			for (c1 = 0; c1 < POINT; c1++) {
				y[c1 * DIMS + c3] = v[c1] * t[c1 * DIMS + c3] + u[c1] * d1 + d2;
			}
		}
		for (eps = 0, c1 = 0; c1 < DIMS * POINT; c1++) {
			eps += pow(x[c1] - y[c1], 2);
		}
		memcpy(x, y, sizeof(double) * DIMS * POINT);
		ct++;
		if (1) { /* Condition for recalculating MDS error, if not every iteration */
			for (cer = 0, c1 = 0, c4 = 0; c1 < POINT - 1; c1++) {
				for (c2 = c1 + 1; c2 < POINT; c2++) {
					for (d1 = 0, c3 = 0; c3 < DIMS; c3++) {
						d1 += pow(x[c1 * DIMS + c3] - x[c2 * DIMS + c3], 2);
					}
					cer += w[c1] * w[c2] * pow(sqrt(d1) - D[c4], 2);
					c4++;
				}
			}
			if (eps < 1e-20) { /* Termination condition */
				break;
			}
			file = tryfopen(name3, "wb");
			fwrite(x, sizeof(double), DIMS * POINT, file);
			fclose(file);
			file = tryfopen(name, "wb");
			fprintf(file, "%d %d %d\n%.16le\n%.16le %.16le\n%.16le\t%.16le\n", ct, *gct, *tct, eps, cer, sqrt(cer / tot), err, sqrt(err / tot));
			fclose(file);
		}
	} while (alive);
	if (!alive) {
		file = tryfopen(name3, "wb");
		fwrite(x, sizeof(double), DIMS * POINT, file);
		fclose(file);
	}
	file = tryfopen(name, "wb");
	if (!alive) {
		fprintf(file, "%d\t%d\t%d\n%.16le\n", ct, *gct, *tct, eps);
	} else {
		*tct += ct;
		fprintf(file, "%d\t%d\t%d\n%.16le\n", -1, *gct, *tct, -1.);
	}
	for (cer = 0, c1 = 0, c4 = 0; c1 < POINT - 1; c1++) {
		for (c2 = c1 + 1; c2 < POINT; c2++) {
			for (d1 = 0, c3 = 0; c3 < DIMS; c3++) {
				d1 += pow(x[c1 * DIMS + c3] - x[c2 * DIMS + c3], 2);
			}
			cer += w[c1] * w[c2] * pow(sqrt(d1) - D[c4], 2);
			c4++;
		}
	}
	if (cer <= err) {
		seterr(cer);
		fprintf(file, "%.16le\t%.16le\n%.16le\t%.16le\n", cer, sqrt(cer / tot), err, sqrt(err / tot));
		fclose(file);
		file = tryfopen(name2, "wb");
		fwrite(x, sizeof(double), DIMS * POINT, file);
		fclose(file);
	} else {
		fprintf(file, "%.16le\t%.16le\n%.16le\t%.16le\n", cer, sqrt(cer / tot), err, sqrt(err / tot));
		fclose(file);
	}
}

void thread(const double* restrict D, const double* restrict v, const double* restrict u, const double* restrict w, const char* name, const char* name2, const char* name3) {
	int c1, ct = -1, gct = 0, tct = 0, tgt = -1;
	double eps = -1, cer = 1e20, d1, ber = 1e20, x[DIMS * POINT];
	FILE* file;
	file = fopen(name, "rb");
	if (file != NULL) {
		fscanf(file, " %d %d %d %le %le %le %le ", &ct, &gct, &tct, &eps, &cer, &d1, &ber);
		seterr(cer);
		seterr(ber);
		fclose(file);
		if (ct >= 0 && eps >= 0) {
			file = tryfopen(name3, "rb");
			fread(x, sizeof(double), DIMS * POINT, file);
			fclose(file);
			iterate(D, v, u, w, x, ct, name, name2, name3, &gct, &tct);
		}
	}
	while (alive) {
		for (c1 = 0; c1 < DIMS * POINT; c1++) {
			x[c1] = ldexp(randMT(), -32);
		}
		iterate(D, v, u, w, x, 0, name, name2, name3, &gct, &tct);
	}
}

int main(int argc, char *argv[]) {
	int c1, c2, c3, c4, ct = 0;
	double *D, v[POINT], u[POINT], w[POINT], d1, d2, cer, ber;
	char name[80], name2[80], name3[80];
	FILE* file;
	if (argc <= 1) {
		exit(-1);
	}
	argc = atoi(argv[1]);
	signal(SIGTERM, handler);
	signal(SIGINT, handler);
	signal(SIGABRT, handler);
	signal(SIGALRM, handler);
	signal(SIGHUP, handler);
	srandMT(time(NULL) + argc * 1024);
	file = tryfopen(RLISTF, "rb");
	for (c1 = 0; c1 < POINT; c1++) {
		fscanf(file, " %d %d ", &c2, &c3);
		w[c1] = c3;
		tot -= w[c1] * w[c1];
	}
	fclose(file);
	tot /= 2;
	D = trymalloc(sizeof(double) * POINT * (POINT - 1) / 2);
	file = tryfopen(RDISTF, "rb");
	if (fread(D, sizeof(double), POINT * (POINT - 1) / 2, file) < POINT * (POINT - 1) / 2) {
		exit(3);
	}
	fclose(file);
	for (c1 = 0, d1 = 0, d2 = 0; c1 < POINT; c1++) {
		d1 += w[c1];
		d2 += 1 / w[c1];
	}
	for (c1 = 0; c1 < POINT; c1++) {
		v[c1] = 1 / d1 / w[c1];
		u[c1] = (d2 / POINT - 2 / w[c1]) / POINT / d1 / 2;
	}
	for (c1 = 0; c1 < 256; c1++) {
		snprintf(name, 80, FNAME1, DIMS, c1);
		file = fopen(name, "rb");
		if (file != NULL) {
			fscanf(file, " %d %d %d %le %le %le %le ", &c2, &c3, &c4, &d1, &cer, &d2, &ber);
			seterr(cer);
			seterr(ber);
			fclose(file);
		}
	}
	snprintf(name, 80, FNAME1, DIMS, argc);
	snprintf(name2, 80, FNAME2, DIMS, argc);
	snprintf(name3, 80, FNAME3, DIMS, argc);
	thread(D, v, u, w, name, name2, name3);
	free(D);
	return 0;
}

