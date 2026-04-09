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
gainrule_camfit_linear.m and gainrule_camfit_compr.m.

These implement the Cambridge fitting rules based on Moore (1998, 1999).

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

from .audiology import isothr, freq_interp_sh, ltass_speech_level


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
