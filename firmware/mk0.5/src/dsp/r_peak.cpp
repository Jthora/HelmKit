// HelmKit Mk0.5 — Streaming R-peak detector implementation.
// See r_peak.h.

#include "dsp/r_peak.h"

#include <math.h>
#include <string.h>

namespace helmkit::dsp {

// Buffer-fit guards. If a future band exceeds these, bump the *Max
// constants in r_peak.h and re-verify the byte-identical PPG gate.
static_assert(rpeak_bands::kPpgDefault.hpf_window      <= RPeakDetector::kHpfWindowMax,
              "PPG hpf_window exceeds kHpfWindowMax");
static_assert(rpeak_bands::kPpgDefault.mwi_window      <= RPeakDetector::kMwiWindowMax,
              "PPG mwi_window exceeds kMwiWindowMax");
static_assert(rpeak_bands::kEcgPanTompkins.hpf_window  <= RPeakDetector::kHpfWindowMax,
              "ECG hpf_window exceeds kHpfWindowMax");
static_assert(rpeak_bands::kEcgPanTompkins.mwi_window  <= RPeakDetector::kMwiWindowMax,
              "ECG mwi_window exceeds kMwiWindowMax");

RPeakDetector::RPeakDetector() : RPeakDetector(rpeak_bands::kPpgDefault) {}

RPeakDetector::RPeakDetector(const RPeakBand& band) : band_(band) { reset(); }

void RPeakDetector::reset() {
    memset(hpf_buf_, 0, sizeof hpf_buf_);
    hpf_idx_ = 0;
    hpf_sum_ = 0.0;
    hpf_warmed_ = false;
    hpf_count_ = 0;

    memset(hist_, 0, sizeof hist_);
    hist_idx_ = 0;

    memset(mwi_buf_, 0, sizeof mwi_buf_);
    mwi_idx_ = 0;
    mwi_sum_ = 0.0;

    spki_ = 0.0f;
    npki_ = 0.0f;
    threshold_ = 0.0f;

    in_peak_ = false;
    peak_amp_ = 0.0f;
    peak_t_ms_ = 0;
    last_accepted_t_ms_ = 0;

    head_ = tail_ = 0;
    memset(&diag_, 0, sizeof diag_);
}

void RPeakDetector::push_peak_(const Peak& p) {
    const size_t next = (tail_ + 1) % kFifoCapacity;
    if (next == head_) {
        // FIFO full: drop oldest to keep the most recent. Loss is noted
        // implicitly via peaks_emitted vs caller consume rate.
        head_ = (head_ + 1) % kFifoCapacity;
    }
    fifo_[tail_] = p;
    tail_ = next;
    diag_.peaks_emitted++;
}

void RPeakDetector::process(uint32_t t_ms, uint32_t sample_raw) {
    diag_.samples_in++;

    const float x = static_cast<float>(sample_raw);

    // ---- (1) High-pass detrend: x - SMA(N) ------------------------------
    hpf_sum_ -= hpf_buf_[hpf_idx_];
    hpf_buf_[hpf_idx_] = x;
    hpf_sum_ += x;
    hpf_idx_ = (hpf_idx_ + 1) % band_.hpf_window;
    if (!hpf_warmed_) {
        if (++hpf_count_ >= band_.hpf_window) hpf_warmed_ = true;
        // While warming, feed zero into downstream so transient settles
        // before threshold learning starts.
        return;
    }
    const float hp = x - static_cast<float>(hpf_sum_ / band_.hpf_window);

    // ---- (2) 3-tap derivative: y[n] = x[n] - x[n-2] ---------------------
    // Buffer convention: hist_idx_ is the NEXT write slot. The slot two
    // samples back is (hist_idx_ + 1) % 3 (i.e. the oldest non-write slot).
    // Warmup: for the first two samples after reset, x[n-2] is 0 and the
    // derivative is dominated by the new sample — acceptable since the
    // HPF warmup already discarded the leading 50 samples.
    const size_t two_back = (hist_idx_ + 1) % 3;
    const float  deriv = hp - hist_[two_back];
    hist_[hist_idx_] = hp;
    hist_idx_ = (hist_idx_ + 1) % 3;

    // ---- (3) Square -----------------------------------------------------
    const float sq = deriv * deriv;

    // ---- (4) Moving-window integration ----------------------------------
    mwi_sum_ -= mwi_buf_[mwi_idx_];
    mwi_buf_[mwi_idx_] = sq;
    mwi_sum_ += sq;
    mwi_idx_ = (mwi_idx_ + 1) % band_.mwi_window;
    const float mwi = static_cast<float>(mwi_sum_ / band_.mwi_window);

    // ---- (5) Adaptive baseline (NPKI) — always learning -----------------
    npki_ = band_.npki_learn_rate * mwi + (1.0f - band_.npki_learn_rate) * npki_;
    threshold_ = npki_ + band_.thresh_fraction * (spki_ - npki_);
    diag_.npki = npki_;
    diag_.spki = spki_;
    diag_.threshold = threshold_;

    // ---- (6) Peak-finder state machine ----------------------------------
    if (!in_peak_) {
        if (mwi > threshold_ && spki_ > 0.0f /* learned at least one */) {
            in_peak_ = true;
            peak_amp_ = mwi;
            peak_t_ms_ = t_ms;
        } else if (mwi > threshold_) {
            // First-ever above-baseline excursion: seed SPKI so the
            // threshold can rise above NPKI on the next sample.
            spki_ = mwi;
            in_peak_ = true;
            peak_amp_ = mwi;
            peak_t_ms_ = t_ms;
        }
    } else {
        if (mwi > peak_amp_) {
            peak_amp_ = mwi;
            peak_t_ms_ = t_ms;
        }
        if (mwi < threshold_ * band_.peak_release_fraction) {
            // End of peak. Decide accept/reject and emit.
            in_peak_ = false;
            spki_ = band_.spki_learn_rate * peak_amp_
                  + (1.0f - band_.spki_learn_rate) * spki_;

            uint16_t rr_ms = 0;
            bool in_range = true;   // first peak counts as in-range
            if (last_accepted_t_ms_ != 0) {
                const uint32_t delta = peak_t_ms_ - last_accepted_t_ms_;
                if (delta < band_.refractory_ms) {
                    diag_.peaks_rejected_refractory++;
                    return;   // suppress entirely; do not advance last_accepted
                }
                // Clamp to uint16 range for wire format.
                rr_ms = (delta > 65535u) ? 65535u : static_cast<uint16_t>(delta);
                in_range = (delta >= band_.rr_min_ms && delta <= band_.rr_max_ms);
            }

            const float conf = (threshold_ > 1e-6f)
                ? (peak_amp_ / threshold_)
                : 1.0f;
            Peak p{ peak_t_ms_, rr_ms, in_range, conf };
            push_peak_(p);
            last_accepted_t_ms_ = peak_t_ms_;
        }
    }
}

Peak RPeakDetector::consume_peak() {
    if (head_ == tail_) {
        return Peak{0, 0, false, 0.0f};
    }
    const Peak p = fifo_[head_];
    head_ = (head_ + 1) % kFifoCapacity;
    return p;
}

}  // namespace helmkit::dsp
