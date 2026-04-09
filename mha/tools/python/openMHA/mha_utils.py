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

"""Utility functions for openMHA configuration.

This module provides a Python equivalent of the MATLAB struct2mhacfg.m
function for converting nested Python dictionaries into MHA-compatible
configuration assignment strings.

Example usage:
    from openMHA.mha_utils import dict_to_mhacfg

    cfg = {
        'fragsize': 64,
        'srate': 44100,
        'mhalib': 'overlapadd',
        'mha': {
            'fftlen': 256,
            'wnd': {'type': 'hanning'},
        },
    }
    assignments = dict_to_mhacfg(cfg)
    # ['fragsize=64', 'srate=44100', 'mha.fftlen=256',
    #  'mha.wnd.type=hanning', 'mhalib=overlapadd']
"""


def value_to_mha_string(value):
    """Convert a Python value to its MHA string representation.

    Parameters
    ----------
    value : str, bool, int, float, complex, list, or tuple
        The Python value to convert.

    Returns
    -------
    str
        The MHA-compatible string representation.

    Raises
    ------
    TypeError
        If the value type is not supported.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return 'yes' if value else 'no'
    if isinstance(value, complex):
        return '({:.17g}{:+.17g}i)'.format(value.real, value.imag)
    if isinstance(value, (int, float)):
        return '{:.17g}'.format(value)
    if isinstance(value, (list, tuple)):
        if not value:
            return '[]'
        first = value[0]
        # 2D matrix: list of lists
        if isinstance(first, (list, tuple)):
            rows = []
            for row in value:
                inner = ' '.join(value_to_mha_string(v) for v in row)
                rows.append('[' + inner + ']')
            return '[ ' + '; '.join(rows) + ' ]'
        # 1D vector
        return '[' + ' '.join(value_to_mha_string(v) for v in value) + ']'
    raise TypeError('Unsupported value type: {}'.format(type(value).__name__))


def dict_to_mhacfg(data, prefix=''):
    """Convert a nested Python dictionary to MHA configuration assignments.

    This is a Python equivalent of MATLAB's struct2mhacfg.m. It recursively
    flattens a nested dictionary into a list of ``"path=value"`` strings,
    sorted by depth. Assignments to ``mhalib`` and ``iolib`` keys are sorted
    after other assignments at the same depth, because they load plugins
    that create sub-parsers needed by deeper assignments.

    Parameters
    ----------
    data : dict or value
        A nested dictionary representing MHA configuration, or a leaf value.
    prefix : str, optional
        A dot-separated path prefix (used internally for recursion).

    Returns
    -------
    list of str
        Sorted list of ``"key=value"`` assignment strings.

    Examples
    --------
    >>> dict_to_mhacfg({'fragsize': 64, 'mhalib': 'overlapadd'})
    ['fragsize=64', 'mhalib=overlapadd']

    >>> dict_to_mhacfg({'mha': {'fftlen': 256}})
    ['mha.fftlen=256']
    """
    assignments = _flatten(data, prefix)
    assignments.sort(key=_sort_key)
    return assignments


def _flatten(data, prefix):
    """Recursively flatten a dict into ``"prefix.key=value"`` strings."""
    if not isinstance(data, dict):
        return ['{}={}'.format(prefix, value_to_mha_string(data))]
    result = []
    for key, val in data.items():
        child_prefix = '{}.{}'.format(prefix, key) if prefix else key
        result.extend(_flatten(val, child_prefix))
    return result


def _sort_key(assignment):
    """Sort key: primary by dot-depth, secondary push mhalib/iolib later."""
    lhs = assignment.split('=', 1)[0]
    depth = lhs.count('.')
    # mhalib/iolib load plugins, so they must come after other assignments
    # at the same depth (the plugin creates the sub-parser for deeper keys)
    plugin_penalty = 1 if lhs.endswith(('mhalib', 'iolib')) else 0
    return (depth, plugin_penalty)
