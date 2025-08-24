/*
 * Kinda-Lang C Fuzzy Logic Runtime
 * Provides probabilistic and fuzzy operations for C code generation
 */

#ifndef KINDA_FUZZY_H
#define KINDA_FUZZY_H

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>

// Initialize random seed for fuzzy operations
static bool __kinda_initialized = false;

static void __kinda_init(void) {
    if (!__kinda_initialized) {
        srand((unsigned int)time(NULL));
        __kinda_initialized = true;
    }
}

// Kinda Int: Fuzzy integer with small random noise
static int kinda_int(int base_value) {
    __kinda_init();
    int fuzz = (rand() % 3) - 1;  // -1, 0, or 1
    return base_value + fuzz;
}

// Kinda Binary: Returns 1, -1, or 0 with specified probabilities
static int kinda_binary_default(void) {
    __kinda_init();
    int rand_val = rand() % 100;
    if (rand_val < 40) return 1;    // 40% positive
    if (rand_val < 80) return -1;   // 40% negative  
    return 0;                       // 20% neutral
}

static int kinda_binary_custom(int pos_prob, int neg_prob) {
    __kinda_init();
    int rand_val = rand() % 100;
    if (rand_val < pos_prob) return 1;
    if (rand_val < pos_prob + neg_prob) return -1;
    return 0;
}

// Fuzzy Assignment: Apply noise to assignment
static int fuzzy_assign(int value) {
    __kinda_init();
    int fuzz = (rand() % 3) - 1;  // -1, 0, or 1
    return value + fuzz;
}

// Sometimes: 50% chance conditional with optional condition check
static bool sometimes_default(void) {
    __kinda_init();
    return (rand() % 2) == 0;  // 50% chance
}

static bool sometimes_with_condition(bool condition) {
    __kinda_init();
    return condition && ((rand() % 2) == 0);
}

// Maybe: 60% chance conditional with optional condition check  
static bool maybe_default(void) {
    __kinda_init();
    return (rand() % 100) < 60;  // 60% chance
}

static bool maybe_with_condition(bool condition) {
    __kinda_init();
    return condition && ((rand() % 100) < 60);
}

// Sorta Print: 80% chance to print, 20% chance to print with [shrug]
#define sorta_print(fmt, ...) do { \
    __kinda_init(); \
    if ((rand() % 100) < 80) { \
        printf("[print] " fmt "\n", ##__VA_ARGS__); \
    } else { \
        printf("[shrug] " fmt "\n", ##__VA_ARGS__); \
    } \
} while(0)

// Convenience macros for common patterns
#define sometimes(cond) sometimes_with_condition(cond)
#define sometimes_random() sometimes_default()
#define maybe(cond) maybe_with_condition(cond) 
#define maybe_random() maybe_default()
#define kinda_binary() kinda_binary_default()

#endif // KINDA_FUZZY_H