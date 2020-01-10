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

#define SIZE   2048			/* Number of automata in the dataset */
#define POINT  500			/* Number of clusters to reduce to */
#define DISTMF "D3LT-80"	/* Filename of the distance matrix */
#define LISTF  "D3LT.list"	/* Filename of the automata list */
#define TREEF  "D3LT.tree"	/* Filename of the unsorted UPGMA tree */
#define UPGMAF "D3LT.upgma"	/* Filename of the sorted UPGMA tree */
#define ORDERF "D3LT.order"	/* Filename of the cluster ordering */
#define RDISTF "D3LT-80r"	/* Filename of the reduced distance matrix */
#define RLISTF "D3LTr.list"	/* Filename of the cluster list */

int getmatrix(int c1, int c2) {
	int c3;
	if (c1 > c2) {
		c3 = c1;
		c1 = c2;
		c2 = c3;
	}
	return SIZE * (SIZE - 1) / 2 - (SIZE - c1) * (SIZE - 1 - c1) / 2 + (c2 - c1) - 1;
}

void treeverse(int node, int *ledge, int *redge, FILE* out) {
	if (ledge[node] >= SIZE) {
		treeverse(ledge[node] - SIZE, ledge, redge, out);
	} else {
		fprintf(out, "%d\n", ledge[node]);
	}
	if (redge[node] >= SIZE) {
		treeverse(redge[node] - SIZE, ledge, redge, out);
	} else {
		fprintf(out, "%d\n", redge[node]);
	}
}

void order() {
	int c1, c2, c3, ct = -1;
	int tree[1000];
	int oedge[SIZE], ledge[SIZE - 1], redge[SIZE - 1];
	double d1;
	FILE* file;
	memset(oedge, -1, sizeof(int) * SIZE);
	memset(ledge, -1, sizeof(int) * (SIZE - 1));
	memset(redge, -1, sizeof(int) * (SIZE - 1));
	file = fopen(UPGMAF, "rb");
	do {
		fscanf(file, " %le %d %d %d ", &d1, &c1, &c2, &c3);
		ct++;
		if (oedge[c1] == -1) {
			oedge[c1] = ct;
			ledge[ct] = c1;
		} else {
			ledge[ct] = oedge[c1] + SIZE;
			oedge[c1] = ct;
		}
		if (oedge[c2] == -1) {
			oedge[c2] = ct;
			redge[ct] = c2;
		} else {
			redge[ct] = oedge[c2] + SIZE;
			oedge[c2] = ct;
		}
	} while (!feof(file));
	fclose(file);
	file = fopen(ORDERF, "wb");
	treeverse(SIZE - 2, ledge, redge, file);
	fclose(file);
}

void reduce() {
	int i, j, k, c1, c2, c3, c4, c5, c6, pt = SIZE, depth;
	int sizer[SIZE], tree1[SIZE - 1], tree2[SIZE - 1], trees[SIZE - 1];
	unsigned long c0;
	double d1, d2, d3, height[SIZE - 1], *matrix;
	FILE* file;
	matrix = malloc(sizeof(double) * SIZE * (SIZE - 1) / 2);
	file = fopen(DISTMF, "rb");
	fread(matrix, sizeof(double), SIZE * (SIZE - 1) / 2, file);
	fclose(file);
	file = fopen(LISTF, "rb");
	for (c1 = 0; c1 < SIZE; c1++) {
		fscanf(file, " %ld %d ", &c0, sizer + c1);
	}
	fclose(file);
	file = fopen(UPGMAF, "rb");
	for (k = 0; k < SIZE - POINT; k++) {
		fscanf(file, " %le %d %d %d ", &d1, &c1, &c2, &c3);
		tree1[SIZE - pt] = c1;
		tree2[SIZE - pt] = c2;
		height[SIZE - pt] = d1;
		trees[SIZE - pt] = sizer[c1] + sizer[c2];
		d1 = (double)sizer[c1] / (sizer[c1] + sizer[c2]);
		d2 = (double)sizer[c2] / (sizer[c1] + sizer[c2]);
		sizer[c1] += sizer[c2];
		sizer[c2] = -1;
		for (i = 0; i < c1; i++) {
			c3 = getmatrix(c1, i);
			c4 = getmatrix(c2, i);
			matrix[c3] = matrix[c3] * d1 + matrix[c4] * d2;
			matrix[c4] = 1.1;
		}
		for (i = c1 + 1; i < c2; i++) {
			c3 = getmatrix(c1, i);
			c4 = getmatrix(c2, i);
			matrix[c3] = matrix[c3] * d1 + matrix[c4] * d2;
			matrix[c4] = 1.1;
		}
		for (i = c2 + 1; i < SIZE; i++) {
			c3 = getmatrix(c1, i);
			c4 = getmatrix(c2, i);
			matrix[c3] = matrix[c3] * d1 + matrix[c4] * d2;
			matrix[c4] = 1.1;
		}
		matrix[getmatrix(c1, c2)] = 1.1;
		pt--;
	}
	fclose(file);
	file = fopen(ORDERF, "rb");
	depth = 0;
	do {
		fscanf(file, " %d ", &c1);
		if (sizer[c1] != -1) {
			tree1[depth] = c1;
			tree2[depth++] = sizer[c1];
		}
	} while (!feof(file));
	fclose(file);
	file = fopen(RLISTF, "wb");
	for (i = 0; i < pt; i++) {
		fprintf(file, "%d %d\n", tree1[i], tree2[i]);
	}
	fclose(file);
	file = fopen(RDISTF, "wb");
	for (i = 0; i < pt - 1; i++) {
		for (j = i + 1; j < pt; j++) {
			fwrite(matrix + getmatrix(tree1[i], tree1[j]), sizeof(double), 1, file);
		}
	}
	fclose(file);
}

void upgma() {
	char alive;
	int i, c1, c2, c3, c4, pt = SIZE, depth;
	int chain[1000], sizer[SIZE], tree1[SIZE - 1], tree2[SIZE - 1], trees[SIZE - 1];
	unsigned long c0;
	double d1, d2, d3, height[SIZE - 1], *matrix;
	FILE* file;
	matrix = malloc(sizeof(double) * SIZE * (SIZE - 1) / 2);
	file = fopen(DISTMF, "rb");
	fread(matrix, sizeof(double), SIZE * (SIZE - 1) / 2, file);
	fclose(file);
	file = fopen(LISTF, "rb");
	for (c1 = 0; c1 < SIZE; c1++) {
		fscanf(file, " %ld %d ", &c0, sizer + c1);
	}
	fclose(file);
	memset(chain, -1, sizeof(int) * 1000);
	depth = -1;
	do {
		if (depth == -1) {
			chain[++depth] = 0;
		}
		alive = 1;
		do {
			c3 = -1;
			d1 = 1.1;
			for (i = 0; i < chain[depth]; i++) {
				d2 = matrix[getmatrix(chain[depth], i)];
				if (d2 < d1) {
					d1 = d2;
					c3 = i;
				}
			}
			for (i = chain[depth] + 1; i < SIZE; i++) {
				d2 = matrix[getmatrix(chain[depth], i)];
				if (d2 < d1) {
					d1 = d2;
					c3 = i;
				}
			}
			chain[++depth] = c3;
			for (i = depth - 1; i >= 0; i--) {
				if (chain[depth] == chain[i]) {
					depth -= 2;
					alive = 0;
					break;
				}
			}
		} while (alive);
		c1 = chain[depth];
		c2 = chain[depth + 1];
		if (c2 < c1) {
			c3 = c1;
			c1 = c2;
			c2 = c3;
		}
		tree1[SIZE - pt] = c1;
		tree2[SIZE - pt] = c2;
		height[SIZE - pt] = d1;
		trees[SIZE - pt] = sizer[c1] + sizer[c2];
		d1 = (double)sizer[c1] / (sizer[c1] + sizer[c2]);
		d2 = (double)sizer[c2] / (sizer[c1] + sizer[c2]);
		sizer[c1] += sizer[c2];
		sizer[c2] = -1;
		for (i = 0; i < c1; i++) {
			c3 = getmatrix(c1, i);
			c4 = getmatrix(c2, i);
			matrix[c3] = matrix[c3] * d1 + matrix[c4] * d2;
			matrix[c4] = 1.1;
		}
		for (i = c1 + 1; i < c2; i++) {
			c3 = getmatrix(c1, i);
			c4 = getmatrix(c2, i);
			matrix[c3] = matrix[c3] * d1 + matrix[c4] * d2;
			matrix[c4] = 1.1;
		}
		for (i = c2 + 1; i < SIZE; i++) {
			c3 = getmatrix(c1, i);
			c4 = getmatrix(c2, i);
			matrix[c3] = matrix[c3] * d1 + matrix[c4] * d2;
			matrix[c4] = 1.1;
		}
		matrix[getmatrix(c1, c2)] = 1.1;
		pt--;
		depth--;
	} while (pt > 1);
	file = fopen(TREEF, "wb");
	for (i = 0; i < SIZE - 1; i++) {
		fprintf(file, "%.16le %5d %5d %5d\n", height[i], tree1[i], tree2[i], trees[i]);
	}
	fclose(file);
}

