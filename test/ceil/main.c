#include <stdint.h>
#include <stdbool.h>

int abc(int64_t input, bool* output);

int main() {
    bool result;

    // Test with different values
    abc(5000, &result);
    abc(100, &result);
    abc(5, &result);

    return 0;
}
