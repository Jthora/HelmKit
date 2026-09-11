// HelmKit Mk0.5 — OLED implementation. See oled.h.

#include "ui/oled.h"

#include <Arduino.h>
#include <Wire.h>
#include <stdio.h>
#include <string.h>

#include "board/pins.h"

namespace helmkit::ui {

namespace {

constexpr uint8_t kAddr = 0x3C;
constexpr uint8_t kW = 128, kH = 64;
uint8_t g_fb[kW * kH / 8];
bool    g_present = false;

// 3x5 font: five rows per glyph, three bits per row (bit 2 = left column).
struct Glyph { char c; uint8_t rows[5]; };
const Glyph kFont[] = {
    {'0', {0b111, 0b101, 0b101, 0b101, 0b111}}, {'1', {0b010, 0b110, 0b010, 0b010, 0b111}},
    {'2', {0b111, 0b001, 0b111, 0b100, 0b111}}, {'3', {0b111, 0b001, 0b111, 0b001, 0b111}},
    {'4', {0b101, 0b101, 0b111, 0b001, 0b001}}, {'5', {0b111, 0b100, 0b111, 0b001, 0b111}},
    {'6', {0b111, 0b100, 0b111, 0b101, 0b111}}, {'7', {0b111, 0b001, 0b001, 0b010, 0b010}},
    {'8', {0b111, 0b101, 0b111, 0b101, 0b111}}, {'9', {0b111, 0b101, 0b111, 0b001, 0b111}},
    {'A', {0b010, 0b101, 0b111, 0b101, 0b101}}, {'B', {0b110, 0b101, 0b110, 0b101, 0b110}},
    {'C', {0b111, 0b100, 0b100, 0b100, 0b111}}, {'D', {0b110, 0b101, 0b101, 0b101, 0b110}},
    {'E', {0b111, 0b100, 0b111, 0b100, 0b111}}, {'F', {0b111, 0b100, 0b111, 0b100, 0b100}},
    {'G', {0b111, 0b100, 0b101, 0b101, 0b111}}, {'H', {0b101, 0b101, 0b111, 0b101, 0b101}},
    {'I', {0b111, 0b010, 0b010, 0b010, 0b111}}, {'J', {0b001, 0b001, 0b001, 0b101, 0b111}},
    {'K', {0b101, 0b101, 0b110, 0b101, 0b101}}, {'L', {0b100, 0b100, 0b100, 0b100, 0b111}},
    {'M', {0b101, 0b111, 0b111, 0b101, 0b101}}, {'N', {0b110, 0b101, 0b101, 0b101, 0b101}},
    {'O', {0b111, 0b101, 0b101, 0b101, 0b111}}, {'P', {0b111, 0b101, 0b111, 0b100, 0b100}},
    {'Q', {0b111, 0b101, 0b101, 0b111, 0b001}}, {'R', {0b111, 0b101, 0b110, 0b101, 0b101}},
    {'S', {0b111, 0b100, 0b111, 0b001, 0b111}}, {'T', {0b111, 0b010, 0b010, 0b010, 0b010}},
    {'U', {0b101, 0b101, 0b101, 0b101, 0b111}}, {'V', {0b101, 0b101, 0b101, 0b101, 0b010}},
    {'W', {0b101, 0b101, 0b111, 0b111, 0b101}}, {'X', {0b101, 0b101, 0b010, 0b101, 0b101}},
    {'Y', {0b101, 0b101, 0b010, 0b010, 0b010}}, {'Z', {0b111, 0b001, 0b010, 0b100, 0b111}},
    {' ', {0b000, 0b000, 0b000, 0b000, 0b000}}, {'.', {0b000, 0b000, 0b000, 0b000, 0b010}},
    {':', {0b000, 0b010, 0b000, 0b010, 0b000}}, {'%', {0b101, 0b001, 0b010, 0b100, 0b101}},
    {'-', {0b000, 0b000, 0b111, 0b000, 0b000}}, {'/', {0b001, 0b001, 0b010, 0b100, 0b100}},
    {'!', {0b010, 0b010, 0b010, 0b000, 0b010}}, {'?', {0b111, 0b001, 0b010, 0b000, 0b010}},
    {'+', {0b000, 0b010, 0b111, 0b010, 0b000}}, {'=', {0b000, 0b111, 0b000, 0b111, 0b000}},
    {'<', {0b001, 0b010, 0b100, 0b010, 0b001}}, {'>', {0b100, 0b010, 0b001, 0b010, 0b100}},
    {'_', {0b000, 0b000, 0b000, 0b000, 0b111}},
};

const Glyph* glyph(char c) {
    if (c >= 'a' && c <= 'z') c = (char)(c - 'a' + 'A');
    for (const auto& g : kFont) if (g.c == c) return &g;
    return &kFont[sizeof kFont / sizeof kFont[0] - 13];   // ' ' for anything unknown
}

inline void put_pixel(int x, int y) {
    if (x < 0 || y < 0 || x >= kW || y >= kH) return;
    g_fb[(y / 8) * kW + x] |= (uint8_t)(1 << (y & 7));
}

// Draw at 2x: each glyph 6x10 px, advance 8 px -> 16 columns per line.
void draw_text(int x0, int y0, const char* s) {
    int x = x0;
    for (; *s; ++s) {
        const Glyph* g = glyph(*s);
        for (int r = 0; r < 5; ++r) {
            for (int c = 0; c < 3; ++c) {
                if (g->rows[r] & (1 << (2 - c))) {
                    put_pixel(x + 2 * c, y0 + 2 * r);     put_pixel(x + 2 * c + 1, y0 + 2 * r);
                    put_pixel(x + 2 * c, y0 + 2 * r + 1); put_pixel(x + 2 * c + 1, y0 + 2 * r + 1);
                }
            }
        }
        x += 8;
        if (x >= kW) break;
    }
}

void cmd(uint8_t c) {
    Wire.beginTransmission(kAddr);
    Wire.write((uint8_t)0x00);
    Wire.write(c);
    Wire.endTransmission();
}

void clear() { memset(g_fb, 0, sizeof g_fb); }

void row(uint8_t r, const char* text) { draw_text(0, r * 11, text); }

}  // namespace

bool oled_begin() {
    pinMode(pins::kVextCtrl, OUTPUT);
    digitalWrite(pins::kVextCtrl, LOW);          // Vext on (powers the panel)
    delay(10);
    pinMode(pins::kOledRst, OUTPUT);
    digitalWrite(pins::kOledRst, LOW);
    delay(20);
    digitalWrite(pins::kOledRst, HIGH);
    delay(20);
    Wire.begin(pins::kOledSda, pins::kOledScl, 400000);
    Wire.beginTransmission(kAddr);
    if (Wire.endTransmission() != 0) { g_present = false; return false; }
    const uint8_t init[] = {0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40, 0x8D, 0x14, 0x20, 0x00,
                            0xA1, 0xC8, 0xDA, 0x12, 0x81, 0xCF, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6, 0xAF};
    for (uint8_t c : init) cmd(c);
    g_present = true;
    clear();
    oled_flush();
    return true;
}

bool oled_present() { return g_present; }

void oled_flush() {
    if (!g_present) return;
    cmd(0x21); cmd(0); cmd(kW - 1);              // column range
    cmd(0x22); cmd(0); cmd(7);                   // page range
    for (size_t i = 0; i < sizeof g_fb; i += 32) {
        Wire.beginTransmission(kAddr);
        Wire.write((uint8_t)0x40);
        Wire.write(g_fb + i, 32);
        Wire.endTransmission();
    }
}

void oled_text(uint8_t r, const char* text) {
    if (r > 5) return;
    row(r, text);
}

void oled_status(const OledStatus& s) {
    if (!g_present) return;
    clear();
    char line[24];
    snprintf(line, sizeof line, "%-10.10s  T:%02lu", s.mode, (unsigned long)(s.tally % 100));
    row(0, line);
    if (s.hr_bpm > 0.0f && s.breaths > 0.0f)      snprintf(line, sizeof line, "HR %3.0f  BR %2.0f", (double)s.hr_bpm, (double)s.breaths);
    else if (s.hr_bpm > 0.0f)                     snprintf(line, sizeof line, "HR %3.0f  BR --", (double)s.hr_bpm);
    else if (s.breaths > 0.0f)                    snprintf(line, sizeof line, "HR --   BR %2.0f", (double)s.breaths);
    else                                          snprintf(line, sizeof line, "HR --   BR --");
    row(1, line);
    auto qs = [](char q) -> const char* { return q == 'O' ? "OK" : (q == 'G' ? "GAP" : (q == 'B' ? "BAD" : "--")); };
    snprintf(line, sizeof line, "P:%s T:%s E:%s", qs(s.q_ppg), qs(s.q_thermo), qs(s.q_eda));
    row(2, line);
    if (s.batt_known) snprintf(line, sizeof line, "I:%s  BAT %3u%%", qs(s.q_imu), (unsigned)s.batt_pct);
    else              snprintf(line, sizeof line, "I:%s  BAT --", qs(s.q_imu));
    row(3, line);
    snprintf(line, sizeof line, "LINK %-4.4s DROP %lu", s.link, (unsigned long)(s.drops > 9999 ? 9999 : s.drops));
    row(4, line);
    row(5, s.in_session ? "SESSION LIVE" : "HELMKIT MK0.5");
    oled_flush();
}

void oled_fault(const char* title, const char* line2, const char* line3) {
    if (!g_present) return;
    clear();
    row(0, "FAULT");
    row(1, title ? title : "");
    row(2, line2 ? line2 : "");
    row(3, line3 ? line3 : "");
    row(5, "HELMKIT MK0.5");
    oled_flush();
}

}  // namespace helmkit::ui
