#include <stdint.h>
#include <stdbool.h>

typedef struct CHpoints {
    int field0;
    struct { int x; int y; } p;
    int field2;
    void* ptr1;
    void* ptr2;
} CHpoints;

void abc(CHpoints* chp, int arg1, void** arg2_ptr, int64_t arg3, bool* result);

int main() {
    CHpoints chp;
    bool result;

    // Test with non-null pointer (use 0 instead of NULL)
    void* test1[2] = {(void*)1, (void*)0};
    abc(&chp, 0, test1, 0, &result);
    if (result) return 1;  // Should be false

    // Test with null pointer (use 0 instead of NULL)
    void* test2[2] = {(void*)0, (void*)0};
    abc(&chp, 0, test2, 0, &result);
    if (!result) return 2;  // Should be true

    return 0;
}
