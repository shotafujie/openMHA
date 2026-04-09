# This file is part of the HörTech Open Master Hearing Aid (openMHA)
# Copyright © 2024 Hörzentrum Oldenburg gGmbH
#
# openMHA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# openMHA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License, version 3 for more details.
#
# You should have received a copy of the GNU Affero General Public License,
# version 3 along with openMHA.  If not, see <http://www.gnu.org/licenses/>.

"""Pure-computation audiology utility functions.

Python equivalents of openMHA's MATLAB audiology utilities (Layer 0):
isothr.m, freq_interp_sh.m, range_intersection.m, and
LTASS_speech_level_in_frequency_bands.m.

These functions have no dependencies on MHA connections or external
libraries beyond the Python standard library.

Example usage:
    from openMHA.audiology import isothr, freq_interp_sh

    # Get ISO hearing thresholds at audiometric frequencies
    freqs = [250, 500, 1000, 2000, 4000, 8000]
    thresholds = isothr(freqs)

    # Interpolate audiogram to new frequencies
    new_freqs = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
    interp_htl = freq_interp_sh(freqs, thresholds, new_freqs)
"""

import math

# ISO 226:2003 (20-12500 Hz) + ISO 389-7:2005 (14000-18000 Hz) threshold data
# Values at 0 and 20000 Hz are extrapolated, not from ISO standards.
_ISO_FREQ = [
    0, 20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315,
    400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000,
    5000, 6300, 8000, 10000, 12500, 14000, 16000, 18000, 20000,
]
_ISO_THR = [
    80.0, 78.5, 68.7, 59.5, 51.1, 44.0, 37.5, 31.5, 26.5, 22.1,
    17.9, 14.4, 11.4, 8.6, 6.2, 4.4, 3.0, 2.2, 2.4, 3.5, 1.7,
    -1.3, -4.2, -6.0, -5.4, -1.5, 6.0, 12.6, 13.9, 12.3,
    18.4, 40.2, 73.2, 70.0,
]

# LTASS data from Byrne et al. (1994) J. Acoust. Soc. Am. 96(4) 2108-2120
# Third-octave band levels for speech at 70 dB SPL overall
LTASS_FREQ = [
    63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
    1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000,
    10000, 12500, 16000,
]
_LTASS_EDGE_FREQ = (
    [0.0]
    + [math.sqrt(LTASS_FREQ[i] * LTASS_FREQ[i + 1])
       for i in range(len(LTASS_FREQ) - 1)]
    + [16000 * 2 ** (1 / 6)]
)
_LTASS_LEV = [
    38.6, 43.5, 54.4, 57.7, 56.8, 60.2, 60.3, 59.0, 62.1, 62.1,
    60.5, 56.8, 53.7, 53.0, 52.0, 48.7, 48.1, 46.8, 45.6, 44.5,
    44.3, 43.7, 43.4, 41.3, 40.7,
]
_LTASS_INTENSITY = [10 ** (lev / 10) for lev in _LTASS_LEV]


def _interp1_linear(x_data, y_data, x_query):
    """Linear interpolation with extrapolation (like MATLAB interp1 'extrap')."""
    n = len(x_data)
    if n < 2:
        raise ValueError("Need at least 2 data points for interpolation")

    results = []
    for xq in x_query:
        # Find bracketing interval
        if xq <= x_data[0]:
            # Extrapolate below
            slope = (y_data[1] - y_data[0]) / (x_data[1] - x_data[0])
            results.append(y_data[0] + slope * (xq - x_data[0]))
        elif xq >= x_data[-1]:
            # Extrapolate above
            slope = (y_data[-1] - y_data[-2]) / (x_data[-1] - x_data[-2])
            results.append(y_data[-1] + slope * (xq - x_data[-1]))
        else:
            # Binary search for interval
            lo, hi = 0, n - 1
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if x_data[mid] <= xq:
                    lo = mid
                else:
                    hi = mid
            t = (xq - x_data[lo]) / (x_data[hi] - x_data[lo])
            results.append(y_data[lo] + t * (y_data[hi] - y_data[lo]))
    return results


def isothr(frequencies=None):
    """Return ISO hearing threshold levels in dB SPL.

    Values from 20-12500 Hz are from ISO 226:2003(E). Values from
    14000-18000 Hz are from ISO 389-7:2005. Values at 0 and 20000 Hz
    are extrapolated.

    This is a Python equivalent of MATLAB's isothr.m.

    Parameters
    ----------
    frequencies : list of float, optional
        Frequencies in Hz at which to interpolate thresholds.
        If None, returns the raw ISO data at standard frequencies.

    Returns
    -------
    thresholds : list of float
        Hearing threshold levels in dB SPL.
    frequencies_out : list of float
        The frequencies corresponding to the thresholds (same as input
        if provided, otherwise the standard ISO frequencies).
    """
    if frequencies is None:
        return list(_ISO_THR), list(_ISO_FREQ)

    freq = list(frequencies)
    for i, f in enumerate(freq):
        if f < 50:
            freq[i] = 50

    thresholds = _interp1_linear(_ISO_FREQ, _ISO_THR, freq)
    return thresholds, freq


def freq_interp_sh(f_in, y_in, f):
    """Linear interpolation on logarithmic frequency scale with sample-and-hold.

    Interpolates values linearly in the log-frequency domain. At the
    edges, the boundary values are held constant (sample-and-hold)
    by adding virtual data points at 0.5*f_min and 2*f_max.

    This is a Python equivalent of MATLAB's freq_interp_sh.m.

    Parameters
    ----------
    f_in : list of float
        Input frequencies in Hz (must be positive).
    y_in : list of float
        Values at the input frequencies.
    f : list of float
        Target frequencies at which to interpolate.

    Returns
    -------
    list of float
        Interpolated values at the target frequencies.
    """
    eps = 1e-15
    f_in = [max(eps, fi) for fi in f_in]

    # Add boundary points for sample-and-hold behavior
    log_f_extended = (
        [math.log(0.5 * f_in[0])]
        + [math.log(fi) for fi in f_in]
        + [math.log(2 * f_in[-1])]
    )
    y_extended = [y_in[0]] + list(y_in) + [y_in[-1]]

    log_f_query = [math.log(fi) for fi in f]
    return _interp1_linear(log_f_extended, y_extended, log_f_query)


def range_intersection(r1, r2):
    """Compute the intersection of two numeric ranges.

    Each range is a tuple (lower_inclusive, upper_exclusive). If the
    ranges do not overlap, returns a zero-width range where lower == upper.

    This is a Python equivalent of MATLAB's range_intersection.m.

    Parameters
    ----------
    r1 : tuple of (float, float)
        First range as (lower, upper).
    r2 : tuple of (float, float)
        Second range as (lower, upper).

    Returns
    -------
    tuple of (float, float)
        The intersection range.
    """
    if len(r1) != 2 or len(r2) != 2:
        raise ValueError("Ranges must be 2-element sequences")
    if any(math.isnan(v) for v in (*r1, *r2)):
        raise ValueError("Ranges must not contain NaN")

    lower = max(r1[0], r2[0])
    upper = min(r1[1], r2[1])
    if upper < lower:
        upper = lower
    return (lower, upper)


def ltass_speech_level(edge_frequencies, target_level):
    """Compute speech levels in frequency bands for an LTASS-shaped signal.

    Distributes the energy of a long-term average speech spectrum (LTASS)
    across arbitrary filterbank bands, adjusting for a given broadband level.

    This is a Python equivalent of MATLAB's
    LTASS_speech_level_in_frequency_bands.m.

    Parameters
    ----------
    edge_frequencies : list of float
        Band edge frequencies in Hz (length = num_bands + 1).
    target_level : float
        Desired broadband level in dB SPL.

    Returns
    -------
    levels : list of float
        Per-band levels in dB SPL.
    portions : list of list of float
        Matrix [num_ltass_bands x num_bands] of overlap portions.
    """
    num_bands = len(edge_frequencies) - 1
    if num_bands < 1:
        raise ValueError("At least two edge frequencies are required")

    levels = [0.0] * num_bands
    portions = [[0.0] * num_bands for _ in range(len(LTASS_FREQ))]

    for band in range(num_bands):
        f_range = (edge_frequencies[band], edge_frequencies[band + 1])
        intensity_sum = 0.0

        for ltass_band in range(len(LTASS_FREQ)):
            ltass_range = (
                _LTASS_EDGE_FREQ[ltass_band],
                _LTASS_EDGE_FREQ[ltass_band + 1],
            )
            intersection = range_intersection(f_range, ltass_range)
            ltass_width = ltass_range[1] - ltass_range[0]
            portion = (intersection[1] - intersection[0]) / ltass_width
            portions[ltass_band][band] = portion
            intensity_sum += _LTASS_INTENSITY[ltass_band] * portion

        if intensity_sum > 0:
            levels[band] = 10 * math.log10(intensity_sum) + (target_level - 70)
        else:
            levels[band] = float('-inf')

    return levels, portions
