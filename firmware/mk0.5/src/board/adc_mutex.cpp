// HelmKit Mk0.5 — ADC1 arbitration mutex (definition).
// See adc_mutex.h for rationale.

#include "board/adc_mutex.h"

namespace helmkit::board {

namespace {
SemaphoreHandle_t g_adc1_mutex = nullptr;
}  // namespace

bool adc1_init() {
    if (g_adc1_mutex == nullptr) {
        g_adc1_mutex = xSemaphoreCreateMutex();
    }
    return g_adc1_mutex != nullptr;
}

bool adc1_acquire(uint32_t timeout_ms) {
    // Defensive lazy-init in case caller forgot adc1_init().
    if (g_adc1_mutex == nullptr) adc1_init();
    if (g_adc1_mutex == nullptr) return false;
    return xSemaphoreTake(g_adc1_mutex, pdMS_TO_TICKS(timeout_ms)) == pdTRUE;
}

void adc1_release() {
    if (g_adc1_mutex == nullptr) return;
    xSemaphoreGive(g_adc1_mutex);
}

}  // namespace helmkit::board
