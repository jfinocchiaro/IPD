/* Copyright (C) 2014 Jeffrey Tsang
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
extern void dgesv_(const int *n, const int *nrhs, const double *a, const int *lda, int *ipiv, double *b, const int *ldb, int *info);

#define SIZE  2048		/* Number of automata in the dataset */
#define MSIZE 16769024	/* Size of the matrix in bytes = SIZE * (SIZE - 1) * 4 */
#define CHUNK 1			/* Number of 8MB chunks in the matrix = floor(MSIZE / 2^23) */
#define REMN  1047552	/* Values in the final chunk of the matrix = (MSIZE MOD 2^23) / 8 */
#define STATE 8			/* Number of states in each automaton, only 1-8 supported */

typedef struct {
	char n[STATE * 2 + 1];
} table;

void populate(double* A, double* q, double y, double z, double alpha, const table p) {
	int c1, c2, c3;
	memset(A, 0, sizeof(double) * STATE * STATE * 16);
	memset(q, 0, sizeof(double) * STATE * 8);
	c1 = p.n[0] & 1;
	q[c1 * 2] = 1 - alpha;
	q[STATE * 4 + c1 * 2 + 1] = 1 - alpha;
	for (c1 = 0; c1 < STATE; c1++) {
		c2 = p.n[c1 + 1] & 15;
		c3 = (p.n[c1 + 1] >> 4) & 15;
		A[STATE * 4 * c1 * 4 + c2 * 2] = -y * alpha;
		A[STATE * 4 * c1 * 4 + c2 * 2 + 1] = (y - 1) * alpha;
		A[STATE * 4 * (c1 * 4 + 1) + c3 * 2] = -y * alpha;
		A[STATE * 4 * (c1 * 4 + 1) + c3 * 2 + 1] = (y - 1) * alpha;
		A[STATE * 4 * (c1 * 4 + 2) + c2 * 2] = -z * alpha;
		A[STATE * 4 * (c1 * 4 + 2) + c2 * 2 + 1] = (z - 1) * alpha;
		A[STATE * 4 * (c1 * 4 + 3) + c3 * 2] = -z * alpha;
		A[STATE * 4 * (c1 * 4 + 3) + c3 * 2 + 1] = (z - 1) * alpha;
	}
	for (c1 = 0; c1 < STATE * 4; c1++) {
		A[c1 * (STATE * 4 + 1)] += 1;
	}
}

void point(double y, double z, double alpha, const table p, double out[8]) {
	int c1, ipiv[STATE * 4];
	double A[STATE * STATE * 16], q[STATE * 8];
	const int ns = STATE * 4, nrhs = 2;
	populate(A, q, y, z, alpha, p);	/* IMPORTANT: change to the correct version of populate depending on the representation */
	dgesv_(&ns, &nrhs, A, &ns, ipiv, q, &ns, &c1);
	for (c1 = 0; c1 < 4; c1++) {
#if STATE == 1
		out[c1] = q[c1];
		out[c1 + 4] = q[c1 + 4];
#elif STATE == 2
		out[c1] = q[c1] + q[c1 + 4];
		out[c1 + 4] = q[c1 + 8] + q[c1 + 12];
#elif STATE == 3
		out[c1] = (q[c1] + q[c1 + 4]) + q[c1 + 8];
		out[c1 + 4] = (q[c1 + 12] + q[c1 + 16]) + q[c1 + 20];
#elif STATE == 4
		out[c1] = (q[c1] + q[c1 + 4]) + (q[c1 + 8] + q[c1 + 12]);
		out[c1 + 4] = (q[c1 + 16] + q[c1 + 20]) + (q[c1 + 24] + q[c1 + 28]);
#elif STATE == 5
		out[c1] = ((q[c1] + q[c1 + 4]) + q[c1 + 8]) + (q[c1 + 12] + q[c1 + 16]);
		out[c1 + 4] = ((q[c1 + 20] + q[c1 + 24]) + q[c1 + 28]) + (q[c1 + 32] + q[c1 + 36]);
#elif STATE == 6
		out[c1] = ((q[c1] + q[c1 + 4]) + q[c1 + 8]) + ((q[c1 + 12] + q[c1 + 16]) + q[c1 + 20]);
		out[c1 + 4] = ((q[c1 + 24] + q[c1 + 28]) + q[c1 + 32]) + ((q[c1 + 36] + q[c1 + 40]) + q[c1 + 44]);
#elif STATE == 7
		out[c1] = ((q[c1] + q[c1 + 4]) + (q[c1 + 8] + q[c1 + 12])) + ((q[c1 + 16] + q[c1 + 20]) + q[c1 + 24]);
		out[c1 + 4] = ((q[c1 + 28] + q[c1 + 32]) + (q[c1 + 36] + q[c1 + 40])) + ((q[c1 + 44] + q[c1 + 48]) + q[c1 + 52]);
#elif STATE == 8
		out[c1] = ((q[c1] + q[c1 + 4]) + (q[c1 + 8] + q[c1 + 12])) + ((q[c1 + 16] + q[c1 + 20]) + (q[c1 + 24] + q[c1 + 28]));
		out[c1 + 4] = ((q[c1 + 32] + q[c1 + 36]) + (q[c1 + 40] + q[c1 + 44])) + ((q[c1 + 48] + q[c1 + 52]) + (q[c1 + 56] + q[c1 + 60]));
#endif
	}
}

void evaluate(double y, double y2, double z, double z2, double alpha, const table p, int depth, double* out) {
	const double pc = sqrt(1.0 / 3);
	if (depth) {
		evaluate(y, (y + y2) / 2, z, (z + z2) / 2, alpha, p, depth - 1, out);
		evaluate((y + y2) / 2, y2, z, (z + z2) / 2, alpha, p, depth - 1, out + (8 << (depth * 2)));
		evaluate(y, (y + y2) / 2, (z + z2) / 2, z2, alpha, p, depth - 1, out + (16 << (depth * 2)));
		evaluate((y + y2) / 2, y2, (z + z2) / 2, z2, alpha, p, depth - 1, out + (24 << (depth * 2)));
		return;
	}
	point((y * (1 - pc) + y2 * (1 + pc)) / 2, (z * (1 - pc) + z2 * (1 + pc)) / 2, alpha, p, out);
	point((y * (1 + pc) + y2 * (1 - pc)) / 2, (z * (1 - pc) + z2 * (1 + pc)) / 2, alpha, p, out + 8);
	point((y * (1 - pc) + y2 * (1 + pc)) / 2, (z * (1 + pc) + z2 * (1 - pc)) / 2, alpha, p, out + 16);
	point((y * (1 + pc) + y2 * (1 - pc)) / 2, (z * (1 + pc) + z2 * (1 - pc)) / 2, alpha, p, out + 24);
}

double idiff(const double y[8], const double z[8]) {
	int c1;
	double x[8];
	for (c1 = 0; c1 < 8; c1++) {
		x[c1] = y[c1] - z[c1];
	}
	for (c1 = 0; c1 < 4; c1++) {
		if ((x[c1] < 0) ^ (x[c1 + 4] < 0)) {
			x[c1] = fabs((x[c1] * x[c1] + x[c1 + 4] * x[c1 + 4]) / (x[c1] - x[c1 + 4]));
		} else {
			x[c1] = fabs(x[c1] + x[c1 + 4]);
		}
	}
	return (x[0] + x[1]) + (x[2] + x[3]);
}

double integrate(const double* y, const double* z, int depth) {
	if (depth) {
		return integrate(y, z, depth - 1) + integrate(y + (4 << depth), z + (4 << depth), depth - 1);
	}
	return idiff(y, z);
}

inline void namefile(char name[80], int file, int depth) {
	int c1;
	snprintf(name, 80, "/scratch/jtsang/d8st/d8st-80-");
	for (c1 = 0; c1 < depth; c1++) {
		name[29 + c1] = ((file >> (depth - 1 - c1)) & 1) ? '1' : '0';
	}
	name[29 + c1] = '\0';
}

inline int checkdone(int file, int depth) {
	int c1;
	char name[80];
	for (c1 = depth; c1 >= 0; c1--) {
		namefile(name, file, c1);
		if (!access(name, F_OK)) {
			return 1;
		}
		file >>= 1;
	}
	return 0;
}

void compile(double *hold[SIZE], int file) {
	int c1, c2;
	double val;
	char name[80];
	FILE* out;
	namefile(name, file, 12);
	for (c1 = 0; c1 < 100; c1++) {
		out = fopen(name, "wb");
		if (out) {
			break;
		}
		sleep(5);
	}
	if (c1 == 100) {
		exit(1);
	}
	for (c1 = 0; c1 < SIZE; c1++) {
		for (c2 = c1 + 1; c2 < SIZE; c2++) {
			val = ldexp(integrate(hold[c1], hold[c2], 8), -10);
			if (fwrite(&val, sizeof(double), 1, out) < 1) {
				fclose(out);
				remove(name);
				exit(4);
			}
		}
	}
	fclose(out);
}

void combine(int file, int depth) {
	int c1, c2;
	double *buf1, *buf2;
	char name[80];
	FILE *in1, *in2, *out;
	if ((buf1 = malloc(sizeof(double) * 1048576)) == NULL) {
		exit(2);
	}
	if ((buf2 = malloc(sizeof(double) * 1048576)) == NULL) {
		exit(2);
	}
	namefile(name, file << 1, depth + 1);
	for (c1 = 0; c1 < 100; c1++) {
		in1 = fopen(name, "rb");
		if (in1) {
			break;
		}
		sleep(5);
	}
	if (c1 == 100) {
		exit(1);
	}
	namefile(name, (file << 1) | 1, depth + 1);
	for (c1 = 0; c1 < 100; c1++) {
		in2 = fopen(name, "rb");
		if (in2) {
			break;
		}
		sleep(5);
	}
	if (c1 == 100) {
		fclose(in1);
		exit(1);
	}
	namefile(name, file, depth);
	for (c1 = 0; c1 < 100; c1++) {
		out = fopen(name, "wb");
		if (out) {
			break;
		}
		sleep(5);
	}
	if (c1 == 100) {
		fclose(in1); fclose(in2);
		remove(name);
		exit(1);
	}
	for (c1 = 0; c1 < CHUNK; c1++) {
		if (fread(buf1, sizeof(double), 1048576, in1) < 1048576) {
			exit(3);
		}
		if (fread(buf2, sizeof(double), 1048576, in2) < 1048576) {
			exit(3);
		}
		for (c2 = 0; c2 < 1048576; c2++) {
			buf1[c2] = ldexp(buf1[c2] + buf2[c2], -1);
		}
		if (fwrite(buf1, sizeof(double), 1048576, out) < 1048576) {
			fclose(out);
			remove(name);
			exit(4);
		}
	}
	if (fread(buf1, sizeof(double), REMN, in1) < REMN) {
		exit(3);
	}
	if (fread(buf2, sizeof(double), REMN, in2) < REMN) {
		exit(3);
	}
	fclose(in1);
	fclose(in2);
	for (c2 = 0; c2 < REMN; c2++) {
		buf1[c2] = ldexp(buf1[c2] + buf2[c2], -1);
	}
	if (fwrite(buf1, sizeof(double), REMN, out) < REMN) {
		fclose(out);
		remove(name);
		exit(4);
	}
	fclose(out);
	free(buf1); free(buf2);
	namefile(name, file << 1, depth + 1);
	remove(name);
	namefile(name, (file << 1) | 1, depth + 1);
	remove(name);
}

int main(int argc, char *argv[]) {
	int c1, c2, c3;
	double y = 0, y2 = 1, z = 0, z2 = 1, alpha = 0.8, *hold[SIZE];
	char buffer[80];
	table tp[SIZE];
	FILE* out;
	struct stat ask;
	if (argc <= 1) {
		exit(-1);
	}
	argc = atoi(argv[1]);
	if (argc < 0 || argc >= 1024) {
		exit(-1);
	}
	out = fopen("sample-D8ST", "rb");
	for (c1 = 0; c1 < SIZE; c1++) {
		fgets(buffer, 80, out);
		tp[c1].n[0] = (buffer[0] - '0') & 1;
		for (c2 = 0; c2 < 8; c2++) {
			tp[c2].n[c2 + 1] = (((buffer[c2 * 4 + 1] - '0') & 7) << 1) | ((buffer[c2 * 4 + 2] - '0') & 1) | (((buffer[c2 * 4 + 3] - '0') & 7) << 5) | (((buffer[c2 * 4 + 4] - '0') & 1) << 4);
		}
	}
	fclose(out);
	c3 = argc;
	for (c1 = -5; c1 < 0; c1++) {
		c2 = c3 & 3;
		if (c2 & 2) {
			y += ldexp(1.0, c1);
		} else {
			y2 -= ldexp(1.0, c1);
		}
		if (c2 & 1) {
			z += ldexp(1.0, c1);
		} else {
			z2 -= ldexp(1.0, c1);
		}
		c3 >>= 2;
	}
	for (c1 = 0; c1 < SIZE; c1++) {
		if (!(hold[c1] = malloc(sizeof(double) * 2048))) {
			exit(2);
		}
	}
	if (!checkdone(argc << 2, 12)) {
		for (c1 = 0; c1 < SIZE; c1++) {
			evaluate(y, (y + y2) / 2, z, (z + z2) / 2, alpha, tp[c1], 3, hold[c1]);
		}
		compile(hold, argc << 2);
	}
	if (!checkdone((argc << 2) | 1, 12)) {
		for (c1 = 0; c1 < SIZE; c1++) {
			evaluate(y, (y + y2) / 2, (z + z2) / 2, z2, alpha, tp[c1], 3, hold[c1]);
		}
		compile(hold, (argc << 2) | 1);
	}
	if (!checkdone(argc << 1, 11)) {
		combine(argc << 1, 11);
	}
	if (!checkdone((argc << 2) | 2, 12)) {
		for (c1 = 0; c1 < SIZE; c1++) {
			evaluate((y + y2) / 2, y2, z, (z + z2) / 2, alpha, tp[c1], 3, hold[c1]);
		}
		compile(hold, (argc << 2) | 2);
	}
	if (!checkdone((argc << 2) | 3, 12)) {
		for (c1 = 0; c1 < SIZE; c1++) {
			evaluate((y + y2) / 2, y2, (z + z2) / 2, z2, alpha, tp[c1], 3, hold[c1]);
		}
		compile(hold, (argc << 2) | 3);
	}
	for (c1 = 0; c1 < SIZE; c1++) {
		free(hold[c1]);
	}
	if (!checkdone((argc << 1) | 1, 11)) {
		combine((argc << 1) | 1, 11);
	}
	if (!checkdone(argc, 10)) {
		combine(argc, 10);
	}
	c3 = argc;
	c1 = 9;
	while (c1 > 0 && checkdone(c3 >> 1, c1)) {
		c3 >>= 1;
		c1--;
	}
	for (; c1 >= 0; c1--) {
		c3 >>= 1;
		namefile(buffer, c3 << 1, c1 + 1);
		if (access(buffer, F_OK) || stat(buffer, &ask) || ask.st_size < MSIZE) {
			return 0;
		} else{
		}
		namefile(buffer, (c3 << 1) | 1, c1 + 1);
		if (access(buffer, F_OK) || stat(buffer, &ask) || ask.st_size < MSIZE) {
			return 0;
		}
		namefile(buffer, c3, c1);
		if (!access(buffer, F_OK)) {
			return 0;
		}
		out = fopen(buffer, "wb");
		fwrite(&argc, sizeof(int), 1, out);
		fclose(out);
		sleep(15);
		out = fopen(buffer, "rb");
		fread(&c2, sizeof(int), 1, out);
		fclose(out);
		remove(buffer);
		if (argc != c2) {
			return 5;
		}
		combine(c3, c1);
	}
	return 0;
}

