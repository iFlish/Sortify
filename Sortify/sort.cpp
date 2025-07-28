#include <chrono>
#include <algorithm>

extern "C" {

    void bubble_sort(double* arr, int n, double* elapsed_time_ms) {
        auto start = std::chrono::high_resolution_clock::now();

        for (int i = 0; i < n - 1; ++i) {
            bool swapped = false; // Optimization for early exit
            for (int j = 0; j < n - i - 1; ++j) {
                if (arr[j] > arr[j + 1]) {
                    std::swap(arr[j], arr[j + 1]);
                    swapped = true;
                }
            }
            if (!swapped) break; // Array already sorted
        }

        auto end = std::chrono::high_resolution_clock::now();
        *elapsed_time_ms = std::chrono::duration<double, std::milli>(end - start).count();
    }

    void selection_sort(double* arr, int n, double* elapsed_time_ms) {
        auto start = std::chrono::high_resolution_clock::now();

        for (int i = 0; i < n - 1; ++i) {
            int min_idx = i;
            for (int j = i + 1; j < n; ++j) {
                if (arr[j] < arr[min_idx]) {
                    min_idx = j;
                }
            }
            if (min_idx != i) { // Avoid unnecessary swaps
                std::swap(arr[i], arr[min_idx]);
            }
        }

        auto end = std::chrono::high_resolution_clock::now();
        *elapsed_time_ms = std::chrono::duration<double, std::milli>(end - start).count();
    }

}
