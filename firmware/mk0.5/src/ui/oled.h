// HelmKit Mk0.5 — OLED status and fault pages (Track N, N-U2).
//
// SSD1306 128x64 on the Heltec V3's internal I²C bus 0 (SDA 17, SCL 18,
// RST 21, Vext on GPIO 36 active-low), driven directly over Wire with a
// built-in 3x5 font drawn at 2x: no library, nothing new to pin. Six rows of
// sixteen characters. Refreshed once a second by main; a full flush is
// ~1 KB over I²C at 400 kHz (about 25 ms).
//
// Status page                       Fault page
//   TRANQUIL    T:03                 FAULT
//   HR 142  BR 18                    LOW BATTERY
//   P:OK T:OK E:GAP                  3.41V  SESSION
//   I:--  BAT 78%                    ENDED
//   LINK UP  DROP 0
//   HELMKIT MK0.5

#pragma once

#include <stdint.h>

namespace helmkit::ui {

struct OledStatus {
    const char* mode      = "IDLE";   // mode name, upper-cased on the page
    uint32_t    tally     = 0;
    bool        in_session = false;
    float       hr_bpm    = 0.0f;     // 0 = unknown
    float       breaths   = 0.0f;     // 0 = unknown
    char        q_ppg     = '-';      // 'O' ok, 'G' gap, 'B' bad, '-' off
    char        q_thermo  = '-';
    char        q_eda     = '-';
    char        q_imu     = '-';
    uint8_t     batt_pct  = 0;
    bool        batt_known = false;
    const char* link      = "UP";     // "UP" / "DOWN" / "BUF"
    uint32_t    drops     = 0;
};

bool oled_begin();                        // powers Vext, resets and initialises the panel; false if it does not ACK
bool oled_present();
void oled_status(const OledStatus& s);
void oled_fault(const char* title, const char* line2, const char* line3);
void oled_text(uint8_t row, const char* text);   // raw access for bench diagnostics (row 0..5)
void oled_flush();

}  // namespace helmkit::ui
