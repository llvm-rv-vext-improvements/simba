#include <stdint.h>

void abc(double* array);

int main() {
    double arr[15];

    // Initialize with pattern
    for (int i = 0; i < 15; i++) {
        arr[i] = (double)(i + 1); // 1.0, 2.0, 3.0...
    }

    abc(arr);

    // Quick check of one swap to verify function works
    // If index 1 and 4 were swapped correctly, arr[1] should be 5.0 and arr[4] should be 2.0
    return !(arr[1] == 5.0 && arr[4] == 2.0);
}
