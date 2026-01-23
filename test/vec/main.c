#include <stddef.h>

#define N 64

int checksum(const int* a, size_t n) {
    unsigned int checksum = 0;
    for (int i = 0; i < n; ++i) {
        checksum += (a[i] & 0xFF) ^ (a[i] >> 8);
    }
    return (int)(checksum);
}

int main() {
    int a[N];
    int b[N];
    int c[N];

    for (int i = 0; i < N; ++i) {
        a[i] = i;
        b[i] = N - i;
    }

    for (int i = 0; i < N; ++i) {
        c[i] = (a[i] * b[i]) + 17;
    }

    return checksum(c, N);
}
