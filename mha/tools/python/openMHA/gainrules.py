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

"""Hearing aid gain prescription rules.

Python equivalents of openMHA's MATLAB gain rule functions:
gainrule_camfit_linear.m, gainrule_camfit_compr.m, gainrule_NALRP.m,
gainrule_linear40.m, and gainrule_plack2004.m.

Audiogram format (dict)::

    audiogram = {
        'l': {'htl_ac': {'f': [250, 500, ...], 'hl': [10, 15, ...]}},
        'r': {'htl_ac': {'f': [250, 500, ...], 'hl': [5, 10, ...]}},
    }

Fitmodel format (dict)::

    fitmodel = {
        'frequencies': [250, 500, 1000, ...],      # band center frequencies
        'edge_frequencies': [177, 354, 707, ...],   # band edge frequencies
        'levels': [40, 50, 60, 65, 70, 80, 90],    # input levels in dB SPL
        'side': ['l', 'r'],                         # ears to fit
    }

Example usage:
    from openMHA.gainrules import camfit_linear, camfit_compr

    audiogram = {
        'l': {'htl_ac': {'f': [250, 500, 1000, 2000, 4000, 8000],
                         'hl': [15, 20, 25, 35, 50, 65]}},
        'r': {'htl_ac': {'f': [250, 500, 1000, 2000, 4000, 8000],
                         'hl': [10, 15, 20, 30, 45, 60]}},
    }
    fitmodel = {
        'frequencies': [500, 1000, 2000, 4000],
        'edge_frequencies': [354, 707, 1414, 2828, 5657],
        'levels': [40, 50, 60, 65, 70, 80, 90],
        'side': ['l', 'r'],
    }
    result = camfit_linear(audiogram, fitmodel)
    # result['l'] is a 2D list: [num_levels x num_bands] of gains in dB
"""

import math

from .audiology import isothr, freq_interp_sh, ltass_speech_level, _interp1_linear


def camfit_linear(audiogram, fitmodel, noisegate=45, max_output=100):
    """Linear Cambridge rule for hearing aid fitting.

    Computes frequency-dependent insertion gains as
    ``hearing_loss * 0.48 + intercept``, clamped to non-negative values.
    Gains are further limited so output does not exceed ``max_output``.

    Based on Moore (1998), "Use of a loudness model for hearing-aid
    fitting. I. Linear hearing aids" Brit. J. Audiol. (32) 317-335.

    Python equivalent of MATLAB's gainrule_camfit_linear.m.

    Parameters
    ----------
    audiogram : dict
        Audiogram data with ``audiogram[side]['htl_ac']['f']`` and
        ``audiogram[side]['htl_ac']['hl']`` for each side.
    fitmodel : dict
        Fitting model with ``frequencies``, ``edge_frequencies``,
        ``levels``, and ``side`` keys.
    noisegate : float, optional
        Noise gate level in dB (default 45).
    max_output : float, optional
        Maximum output level in dB (default 100).

    Returns
    -------
    dict
        Gain table with keys for each side (2D list: levels x bands),
        ``insertion_gains`` (dict of 1D lists per side), and
        ``noisegate`` (dict of level/slope per side).
    """
    freqs = fitmodel['frequencies']
    levels = fitmodel['levels']
    num_bands = len(freqs)
    num_levels = len(levels)

    # Cambridge intercepts (defined up to 5 kHz, extended beyond)
    intercept_frequencies = [125, 250, 500, 750, 1000, 1500, 2000, 3000,
                            4000, 5000, 5005]
    intercept_values = [-11, -10, -8, -6, 0, -1, 1, -1, 0, 1, 1]
    intercepts = freq_interp_sh(intercept_frequencies, intercept_values, freqs)

    result = {'insertion_gains': {}, 'noisegate': {}}

    for side in fitmodel['side']:
        htl_data = audiogram.get(side, {}).get('htl_ac', {'f': [], 'hl': []})
        aud_f = htl_data['f']
        aud_hl = htl_data['hl']

        htl = freq_interp_sh(aud_f, aud_hl, freqs)
        insertion_gains = [htl[i] * 0.48 + intercepts[i]
                          for i in range(num_bands)]

        # No negative insertion gains (Moore 1998)
        insertion_gains = [max(0.0, g) for g in insertion_gains]

        # Zero all gains for a 0 dB HL flat audiogram
        if not any(h != 0 for h in htl):
            insertion_gains = [0.0] * num_bands

        result['insertion_gains'][side] = list(insertion_gains)

        # Build gain table: same insertion gain at every level
        gain_table = [list(insertion_gains) for _ in range(num_levels)]

        # Limit output to max_output
        for lev_idx in range(num_levels):
            for band_idx in range(num_bands):
                output = gain_table[lev_idx][band_idx] + levels[lev_idx]
                if output > max_output:
                    gain_table[lev_idx][band_idx] -= (output - max_output)

        result[side] = gain_table

        result['noisegate'][side] = {
            'level': [noisegate] * num_bands,
            'slope': [1.0] * num_bands,
        }

    return result


def _nalrp_gains(htl, fhtl, f):
    """Compute NAL-RP prescribed REIG (dB) at frequencies *f*.

    Internal helper implementing the NalRP.m algorithm.

    Parameters
    ----------
    htl : list of float
        Hearing threshold levels in dB HL.
    fhtl : list of float
        Audiometric frequencies corresponding to *htl*.
    f : list of float
        Target frequencies for the prescription.

    Returns
    -------
    list of float
        Prescribed real-ear insertion gains in dB.
    """
    f_prescr = [250, 500, 1000, 1500, 2000, 3000, 4000, 6000]
    idx500, idx1000, idx2000 = 1, 2, 4  # indices into f_prescr
    gain_zero = [-17, -8, 1, 1, -1, -2, -2, -2]
    gain_factor = 0.31
    gain_factor_m = 0.15
    gain_factor_p = 0.20

    # Severe-loss correction table (Byrne et al 1991, Fig 9)
    h_severe_2000 = [95, 100, 105, 110, 115, 120]
    g_severe = [
        [4, 3, 0, -1, -2, -2, -2, -2],
        [6, 4, 0, -2, -3, -3, -3, -3],
        [8, 5, 0, -3, -5, -5, -5, -5],
        [11, 7, 0, -3, -6, -6, -6, -6],
        [13, 8, 0, -4, -8, -8, -8, -8],
        [15, 9, 0, -5, -9, -9, -9, -9],
    ]

    # Extrapolate audiogram edges
    fhtl_ext = [1.0] + list(fhtl) + [20000.0]
    htl_ext = [htl[0]] + list(htl) + [htl[-1]]

    log_fhtl = [math.log(ff) for ff in fhtl_ext]
    log_fp = [math.log(ff) for ff in f_prescr]
    h_loss = _interp1_linear(log_fhtl, htl_ext, log_fp)

    h_loss_3fa = (h_loss[idx500] + h_loss[idx1000] + h_loss[idx2000]) / 3.0
    g_prescr = [gain_factor * h_loss[i] + gain_factor_m * h_loss_3fa
                + gain_zero[i] for i in range(8)]

    # NAL-RP correction for severe loss
    if h_loss_3fa > 60:
        g_prescr = [g_prescr[i] + gain_factor_p * (h_loss_3fa - 60)
                    for i in range(8)]

    # Extra NAL-RP correction for severe loss at 2 kHz
    if h_loss[idx2000] >= 95:
        corrections = []
        for i in range(8):
            col = [g_severe[row][i] for row in range(6)]
            corr = _interp1_linear(h_severe_2000, col, [h_loss[idx2000]])[0]
            corrections.append(corr)
        g_prescr = [g_prescr[i] + corrections[i] for i in range(8)]

    g_prescr = [max(0.0, g) for g in g_prescr]

    # Extend for extrapolation (zero gain outside prescription range)
    f_ext = [1e-300, 50.0] + f_prescr + [10000.0, 100000.0]
    g_ext = [0.0, 0.0] + g_prescr + [0.0, 0.0]
    log_f_ext = [math.log(ff) for ff in f_ext]
    log_f_out = [math.log(ff) for ff in f]
    return _interp1_linear(log_f_ext, g_ext, log_f_out)


def nalrp(audiogram, fitmodel, noisegate=-40):
    """NAL-RP prescription rule for hearing aid fitting.

    Linear gain rule (same gain at all input levels) using the
    National Acoustic Laboratories' Revised Profound (NAL-RP)
    procedure.

    References:
        Byrne & Dillon (1986). Ear Hearing 7, 257-265. (NAL-R)
        Byrne, Parkinson & Newall (1990). Ear Hearing 11, 40-49.
        Byrne, Parkinson & Newall (1991). The Vanderbilt Hearing Aid
        Report II, York Press, 295-300. (NAL-RP)

    Python equivalent of MATLAB's gainrule_NALRP.m + NalRP.m.

    Parameters
    ----------
    audiogram : dict
        Audiogram data (same format as camfit_linear).
    fitmodel : dict
        Fitting model (same format as camfit_linear).
    noisegate : float, optional
        Noise gate level in dB (default -40).

    Returns
    -------
    dict
        Gain table with keys for each side (2D list: levels x bands),
        and ``noisegate`` (dict of level/slope per side).
    """
    freqs = fitmodel['frequencies']
    levels = fitmodel['levels']
    num_bands = len(freqs)
    num_levels = len(levels)

    result = {'noisegate': {}}

    for side in fitmodel['side']:
        htl_data = audiogram.get(side, {}).get('htl_ac', {'f': [], 'hl': []})
        gains = _nalrp_gains(htl_data['hl'], htl_data['f'], freqs)

        gain_table = [list(gains) for _ in range(num_levels)]
        result[side] = gain_table

        result['noisegate'][side] = {
            'level': [noisegate] * num_bands,
            'slope': [1.0] * num_bands,
        }

    return result


def linear40(audiogram, fitmodel, noisegate=35):
    """Linear 40% hearing-loss rule for hearing aid fitting.

    Prescribes 40% of the hearing loss as insertion gain, constant
    across all input levels (no compression).

    Python equivalent of MATLAB's gainrule_linear40.m.

    Parameters
    ----------
    audiogram : dict
        Audiogram data (same format as camfit_linear).
    fitmodel : dict
        Fitting model (same format as camfit_linear).
    noisegate : float, optional
        Noise gate level in dB (default 35).

    Returns
    -------
    dict
        Gain table with keys for each side (2D list: levels x bands),
        and ``noisegate`` (dict of level/slope per side).
    """
    freqs = fitmodel['frequencies']
    levels = fitmodel['levels']
    num_bands = len(freqs)
    num_levels = len(levels)

    result = {'noisegate': {}}

    for side in fitmodel['side']:
        htl_data = audiogram.get(side, {}).get('htl_ac', {'f': [], 'hl': []})
        htl = freq_interp_sh(htl_data['f'], htl_data['hl'], freqs)
        gains = [0.4 * h for h in htl]

        gain_table = [list(gains) for _ in range(num_levels)]
        result[side] = gain_table

        result['noisegate'][side] = {
            'level': [noisegate] * num_bands,
            'slope': [1.0] * num_bands,
        }

    return result


def _equal_loudness_contour80(frequencies):
    """ISO 226:2003 equal-loudness contour at 80 phon.

    Parameters
    ----------
    frequencies : list of float
        Frequencies in Hz.

    Returns
    -------
    list of float
        Sound pressure levels in dB SPL at each frequency.
    """
    data_f = [20, 30, 40, 50, 60, 80, 100, 200, 300, 400, 600, 900,
              1000, 1600, 2000, 3000, 4000, 5000, 7000, 9000, 10000,
              16000, 18000, 20000]
    data_l = [118, 111, 106, 102, 99, 95, 92, 85, 82, 81, 80, 80,
              80, 82, 80, 78, 79, 84, 90, 93, 93, 85, 84, 90]
    log_f = [math.log(f) for f in data_f]
    log_q = [math.log(f) for f in frequencies]
    return _interp1_linear(log_f, data_l, log_q)


def plack2004(audiogram, fitmodel):
    """Plack (2004) physiologically motivated gain prescription.

    Compressive gain rule based on outer hair cell (OHC) gain loss
    model. Outer and middle ear filter based on ISO 226:2003
    equal-loudness contour at 80 phon.

    Reference:
        Plack, Drga & Lopez-Poveda (2004), "Inferred basilar-membrane
        response functions for listeners with mild to moderate
        sensorineural hearing loss." J. Acoust. Soc. Am. 115(4),
        1684-1695.

    Python equivalent of MATLAB's gainrule_plack2004.m.

    Parameters
    ----------
    audiogram : dict
        Audiogram data (same format as camfit_linear).
    fitmodel : dict
        Fitting model (same format as camfit_linear).

    Returns
    -------
    dict
        Gain table with keys for each side (2D list: levels x bands).
    """
    freqs = fitmodel['frequencies']
    levels = fitmodel['levels']
    num_bands = len(freqs)
    num_levels = len(levels)

    max_ohc_gain = 40.0
    l_min_comp = 25.0
    l_max_comp = 87.0

    eq_n = _equal_loudness_contour80(freqs)
    eq_offset = [eq_n[i] - 80.0 for i in range(num_bands)]

    result = {}

    for side in fitmodel['side']:
        htl_data = audiogram.get(side, {}).get('htl_ac', {'f': [], 'hl': []})
        aud_f = htl_data['f']
        aud_hl = htl_data['hl']

        # Interpolate HTL in log-frequency, clamp to >= 0
        log_aud_f = [math.log(f) for f in aud_f]
        log_fit_f = [math.log(f) for f in freqs]
        htl_interp = _interp1_linear(log_aud_f, aud_hl, log_fit_f)
        htl = [max(0.0, h) for h in htl_interp]

        htl_ohc = [min(max_ohc_gain, h) for h in htl]
        htl_lin = [0.0] * num_bands  # GainLinRatio = 0.0

        gain_table = []
        for lev_idx in range(num_levels):
            row = []
            for k in range(num_bands):
                # Piecewise linear I/O function breakpoints
                compress_range = l_max_comp - l_min_comp
                ohc_ratio = (max_ohc_gain - htl_ohc[k]) / max_ohc_gain
                l3 = l_max_comp - compress_range * ohc_ratio

                pt_l = [l_min_comp - 1 + eq_offset[k],
                        l_min_comp + eq_offset[k],
                        l3 + eq_offset[k],
                        l_max_comp + 1 + eq_offset[k]]
                pt_g = [htl_ohc[k] + htl_lin[k],
                        htl_ohc[k] + htl_lin[k],
                        htl_lin[k],
                        htl_lin[k]]

                # Remove duplicate L values (unique)
                unique_l = []
                unique_g = []
                for i in range(len(pt_l)):
                    if pt_l[i] not in unique_l:
                        unique_l.append(pt_l[i])
                        unique_g.append(pt_g[i])

                gain = _interp1_linear(unique_l, unique_g,
                                       [levels[lev_idx]])[0]
                row.append(gain)
            gain_table.append(row)

        result[side] = gain_table

    return result


def crvar_nalrp(audiogram, fitmodel, compression_ratio=2.0):
    """NAL-RP with variable compression ratio.

    Applies NAL-RP prescribed gains at 65 dB input level and uses
    the specified compression ratio. The knee point is set at the
    LTASS speech level for 40 dB broadband input.

    Python equivalent of MATLAB's gainrule_CRvar_NALRP.m.

    Parameters
    ----------
    audiogram : dict
        Audiogram data (same format as camfit_linear).
    fitmodel : dict
        Fitting model (same format as camfit_linear).
    compression_ratio : float, optional
        Compression ratio (default 2.0, must be >= 1 and < 100).

    Returns
    -------
    dict
        Gain table with keys for each side (2D list: levels x bands),
        and ``compression`` parameters per side.
    """
    if compression_ratio < 1 or compression_ratio >= 100:
        raise ValueError("compression_ratio must be >= 1 and < 100")

    freqs = fitmodel['frequencies']
    levels = fitmodel['levels']
    num_bands = len(freqs)
    num_levels = len(levels)

    c_slope = 1.0 / compression_ratio

    # Knee point and target speech levels in compressor bands
    l_kneepoint, _ = ltass_speech_level(fitmodel['edge_frequencies'], 40)
    l_target, _ = ltass_speech_level(fitmodel['edge_frequencies'], 65)

    result = {'compression': {}}

    for side in fitmodel['side']:
        htl_data = audiogram.get(side, {}).get('htl_ac', {'f': [], 'hl': []})
        g_nalrp = _nalrp_gains(htl_data['hl'], htl_data['f'], freqs)

        # Maximum gain at knee point
        gmax = [g_nalrp[i] + (c_slope - 1) * (l_kneepoint[i] - l_target[i])
                for i in range(num_bands)]

        result['compression'][side] = {
            'gain': list(gmax),
            'l_kneepoint': list(l_kneepoint),
            'c_slope': c_slope,
        }

        # Build gain table
        gain_table = []
        for lev_idx in range(num_levels):
            row = []
            for band in range(num_bands):
                lev = levels[lev_idx]
                if lev < l_kneepoint[band]:
                    gain = gmax[band]
                else:
                    gain = gmax[band] + (lev - l_kneepoint[band]) * (c_slope - 1)
                row.append(gain)
            gain_table.append(row)

        result[side] = gain_table

    return result


def camfit_compr(audiogram, fitmodel, noisegate=45, max_output=100):
    """Compressive Cambridge rule for hearing aid fitting.

    Computes level-dependent gains using compression ratios derived from
    the difference between gains needed for soft and medium-level speech.

    Based on Moore et al. (1999), "Use of a loudness model for hearing
    aid fitting: II. Hearing aids with multi-channel compression."
    Brit. J. Audiol. (33) 157-170.

    Python equivalent of MATLAB's gainrule_camfit_compr.m.

    Parameters
    ----------
    audiogram : dict
        Audiogram data (same format as camfit_linear).
    fitmodel : dict
        Fitting model (same format as camfit_linear).
    noisegate : float, optional
        Noise gate level in dB (default 45).
    max_output : float, optional
        Maximum output level in dB (default 100).

    Returns
    -------
    dict
        Gain table with keys for each side (2D list: levels x bands),
        and ``noisegate`` (dict of level/slope per side).
    """
    freqs = fitmodel['frequencies']
    levels = fitmodel['levels']
    num_bands = len(freqs)
    num_levels = len(levels)

    # Speech levels at 65 dB broadband in the DC bands
    speech_65, _ = ltass_speech_level(fitmodel['edge_frequencies'], 65)
    minima_distance = 38  # dB below 65 dB speech for soft speech minima

    # ISO hearing threshold in SPL for conversion from HL
    conv, _ = isothr(freqs)

    # Compression threshold = level of soft speech minima
    l_min = [speech_65[i] - minima_distance for i in range(num_bands)]

    # Get mid-level gains from linear rule
    linear_result = camfit_linear(audiogram, fitmodel, noisegate, max_output)

    # Mid-level speech band levels
    l_mid = list(speech_65)

    result = {'noisegate': {}}

    for side in fitmodel['side']:
        htl_data = audiogram.get(side, {}).get('htl_ac', {'f': [], 'hl': []})
        aud_f = htl_data['f']
        aud_hl = htl_data['hl']

        htl = freq_interp_sh(aud_f, aud_hl, freqs)

        # Gain needed at compression threshold (soft speech)
        g_min = [htl[i] + conv[i] - l_min[i] for i in range(num_bands)]

        # Linear insertion gains at mid level
        g_mid = linear_result['insertion_gains'][side]

        # Compute compression ratios
        compression_ratio = []
        for i in range(num_bands):
            denominator = (l_mid[i] + g_mid[i]) - (l_min[i] + g_min[i])
            denominator = max(denominator, 13)
            cr = minima_distance / denominator
            cr = max(cr, 1.0)
            compression_ratio.append(cr)

        # Compute gains at each level using compression
        gain_table = []
        for lev_idx in range(num_levels):
            row = []
            for band_idx in range(num_bands):
                compr_thr_output = l_min[band_idx] + g_min[band_idx]
                output = ((levels[lev_idx] - l_min[band_idx])
                          / compression_ratio[band_idx]
                          + compr_thr_output)
                gain = output - levels[lev_idx]
                # No negative gains
                gain = max(0.0, gain)
                # Limit output
                if gain + levels[lev_idx] > max_output:
                    gain = max_output - levels[lev_idx]
                row.append(gain)
            gain_table.append(row)

        # Zero all gains for 0 dB HL flat audiogram
        if not any(h != 0 for h in htl):
            gain_table = [[0.0] * num_bands for _ in range(num_levels)]

        result[side] = gain_table

        result['noisegate'][side] = {
            'level': [noisegate] * num_bands,
            'slope': [1.0] * num_bands,
        }

    return result
