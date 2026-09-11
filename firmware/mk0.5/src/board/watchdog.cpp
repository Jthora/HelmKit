// HelmKit Mk0.5 — task watchdog implementation. See watchdog.h.

#include "board/watchdog.h"

#include <esp_system.h>
#include <esp_task_wdt.h>

namespace helmkit::board {

bool wdt_begin(uint32_t timeout_s) {
    // esp_task_wdt_init reconfigures the global TWDT when it is already
    // running (the core starts it for the idle tasks); panic=true turns a
    // stall into a reset that the next boot attributes as task-wdt.
    const esp_err_t init = esp_task_wdt_init(timeout_s, true);
    if (init != ESP_OK && init != ESP_ERR_INVALID_STATE) return false;
    const esp_err_t add = esp_task_wdt_add(nullptr);          // nullptr = the calling task
    return add == ESP_OK || add == ESP_ERR_INVALID_ARG;        // INVALID_ARG = already subscribed
}

void wdt_feed() {
    esp_task_wdt_reset();
}

const char* reset_reason_str() {
    switch (esp_reset_reason()) {
        case ESP_RST_POWERON:   return "poweron";
        case ESP_RST_EXT:       return "ext";
        case ESP_RST_SW:        return "sw";
        case ESP_RST_PANIC:     return "panic";
        case ESP_RST_INT_WDT:   return "int-wdt";
        case ESP_RST_TASK_WDT:  return "task-wdt";
        case ESP_RST_WDT:       return "wdt";
        case ESP_RST_DEEPSLEEP: return "deepsleep";
        case ESP_RST_BROWNOUT:  return "brownout";
        case ESP_RST_SDIO:      return "sdio";
        case ESP_RST_UNKNOWN:
        default:                return "unknown";
    }
}

int reset_reason_num() {
    return (int)esp_reset_reason();
}

}  // namespace helmkit::board
