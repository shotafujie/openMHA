# This file is part of the HörTech Open Master Hearing Aid (openMHA)
# Copyright © 2020 2021 HörTech gGmbH
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


from ast import literal_eval
from collections.abc import Sequence, MutableSequence
from encodings.utf_8 import encode as encode_utf8
from functools import update_wrapper
import re
import socket

_round_to_square_brackets = str.maketrans('()', '[]')
# This matches either a) digits *not* preceded by an opening parenthesis and
# followed by a space, or b) closing parentheses.  This prevents the
# real-valued part of a complex number from suddenly being separated by a
# comma.
_vcomplex_add_comma = re.compile(br'((?<!\()\d\s|\))')
# This matches complex numbers without a real part, which are not surrounded by
# parentheses.  The purpose is to work around an MHA parser quirk where the
# real part has to be explicitly represented as "0" in the string, e.g.,
# "(0+1.2i)" vs. "1.2i".
_complex_prepend_0 = re.compile(r'([\de\+\.]*\dj(?!\)))')


class _stringify:

    def __init__(self, inputs=True, outputs=True):
        """A decorator that "stringifies" a function.

        This decorator wraps a function "func" that expects bytes arguments and
        returns bytes.  The wrapping function has an identical signature except
        that it automatically encodes str arguments as UTF-8 and also
        automatically decodes the bytes return value.
        """

        self.inputs = inputs
        self.outputs = outputs

    def __call__(self, func):

        def new_func(*args, **kwargs):

            # automatically handle string arguments
            if self.inputs:
                new_args = (
                    (encode_utf8(arg)[0] if isinstance(arg, str) else arg)
                    for arg in args
                )
                new_kwargs = {
                    k: (encode_utf8(v)[0] if isinstance(v, str) else v)
                    for k, v in kwargs.items()
                }
            else:
                new_args = args
                new_kwargs = kwargs

            # optionally return MHA's response as a string
            ret = func(*new_args, **new_kwargs)
            if self.outputs:
                return ret.decode()
            return ret

        # update new_func() to look like func()
        update_wrapper(new_func, func)

        return new_func


class MHAConnection:
    """A class for communicating with a Master Hearing Aid (MHA) instance.

    An instance of this class represents a connection to an MHA process and
    provides a thin abstraction over its network protocol.

    Uses raw TCP sockets (compatible with Python 3.13+, where telnetlib
    has been removed).
    """

    def __init__(self, host="localhost", port=33337, timeout=10):

        self._host = host
        self._port = port
        self._timeout = timeout
        self._sock = socket.create_connection((host, port), timeout=timeout)
        self._buf = b''

        # convenience aliases; defined like this so that they retain the
        # original doc-string and in order to avoid an additional function call
        self.get = self.get_val
        self.set = self.set_val

    def _reopen(self):
        """Close the connection and open it again.
        """

        self._sock.close()
        self._sock = socket.create_connection(
            (self._host, self._port), timeout=self._timeout
        )
        self._buf = b''

    def _recv_until(self, markers):
        """Receive data until one of the byte-string markers is found.

        Returns (index_of_marker, full_response) where index_of_marker
        is the index into the markers list, or -1 on timeout.
        """
        while True:
            for i, marker in enumerate(markers):
                pos = self._buf.find(marker)
                if pos != -1:
                    end = pos + len(marker)
                    resp = self._buf[:end]
                    self._buf = self._buf[end:]
                    return i, resp
            try:
                chunk = self._sock.recv(4096)
            except socket.timeout:
                return -1, self._buf
            if not chunk:
                return -1, self._buf
            self._buf += chunk

    def _send_command(self, buffer, /):
        """Send a command to an MHA instance.

        The argument is a buffer that should be terminated by a newline
        character (b'\\n').
        """

        self._sock.sendall(buffer)
        idx, resp = self._recv_until(
            [b'(MHA:success)', b'(MHA:failure)']
        )
        if idx == 0:
            return resp.rpartition(b'(MHA:success)')[0].strip()
        else:
            raise ValueError(
                'Error sending message {} with error code {}:\nResponse: {}'
                .format(buffer, idx, resp)
            )

    @_stringify()
    def get_contents(self, path=b'', /):
        """Return the contents of the element at "path".
        """

        return self._send_command(path.strip() + b'?\n')

    @_stringify()
    def get_help(self, path, /):
        """Return the documentation of the element at "path".
        """

        return self._send_command(path.strip() + b'?help\n')

    @_stringify()
    def get_type(self, path, /):
        """Return the type of the variable located at "path".
        """

        return self._send_command(path.strip() + b'?type\n')

    @_stringify(outputs=False)
    def is_writable(self, path, /):
        """Return True if the variable located at "path" is writeable.
        """

        ret = self._send_command(path.strip() + b'?perm\n')
        return ret == b'writable'

    def get_val_raw(self, path, /):
        """Return the value of the variable located at "path".
        """

        return self._send_command(path.strip() + b'?val\n')

    @_stringify(outputs=False)
    def get_val(self, path, /):
        """Return the converted value of the variable located at "path".

        This is the same as self.get_val_raw(), except that the value is
        converted to an equivalent Python type.  For example, vector and matrix
        types are converted to Python lists.
        """

        data_type = self.get_type(path)
        data = self.get_val_raw(path)

        # Return MHA's plain strings, booleans and keyword lists immediately
        # since they contain no quotes, which would cause the below
        # literal_eval() to fail.
        if data_type in ['string', 'bool', 'keyword_list']:
            return data.decode()

        # Types returned by OpenMHA contain additional type information (e.g.,
        # matrix<float>), thus we cannot simply check for equality.
        if 'vector' in data_type or 'matrix' in data_type:
            data = data.replace(b' ', b', ')
        elif 'vcomplex' in data_type or 'mcomplex' in data_type:
            data = _vcomplex_add_comma.sub(br'\1,', data) \

        if 'complex' in data_type:
            data = data.replace(b'i', b'j')

        if 'matrix' in data_type or 'mcomplex' in data_type:
            data = data.replace(b';', b',')

        # literal_eval() is a safe version of eval() that only accepts a small
        # list of literal structures
        return literal_eval(data.decode())

    def set_val_raw(self, path, value, /):
        """Set the value of the variable located at "path" to "value".
        """

        cmd = path.strip() + b'=' + value.strip() + b'\n'
        return self._send_command(cmd)

    def set_val(self, path, value, /):
        """Set the value of "path" to "value", after conversion to a string.

        This is the same as self.set_val_raw(), except that the value is
        converted to a string as expected by MHA, e.g., Python sequence types
        are converted to MHA's vector or matrix types (and hence must have at
        most two dimensions!).

        Note: if you want to pass a NumPy array, use its tolist() method.
        """

        if isinstance(path, str):
            path = encode_utf8(path)[0]
        data_type = self.get_type(path)

        if isinstance(value, (str, bytes)):
            pass  # nothing to do
        elif isinstance(value, Sequence):
            if not isinstance(value, MutableSequence):
                value = str(value).translate(_round_to_square_brackets)
            if 'complex' in data_type:
                value = _complex_prepend_0.sub(r'(0+\1)', str(value)) \
                        .replace('j', 'i')
            value = str(value).replace('],', '];').replace(',', ' ')
        elif 'complex' in data_type:
            value = _complex_prepend_0.sub(r'(0+\1)', str(value))
            value = value.replace('j', 'i')
        else:
            value = str(value)

        if isinstance(value, str):
            value = encode_utf8(value)[0]

        return self.set_val_raw(path, value).decode()

    @_stringify()
    def get_range(self, path, /):
        """Return the supported range of values of the variable at "path".
        """

        return self._send_command(path.strip() + b'?range\n')

    @_stringify()
    def get_substitutions(self, path, /):
        """Return the variable substitutions applied to the node at "path".
        """

        return self._send_command(path.strip() + b'?subst\n')

    @_stringify(outputs=False)
    def get_entries(self, path, /):
        """Return the list of nodes under the node at "path".
        """

        resp = self._send_command(path.strip() + b'?entries\n').decode()
        return tuple(resp.strip('[]').split(' '))

    def list_ids(self):
        """Return a dictionary mapping plug-in paths to IDs.
        """

        ids = self._send_command(b'?listid\n').splitlines()
        return dict(id.decode().split(' = ') for id in ids)

    def find_id(self, plugin_id, /):
        """Return a tuple of all plug-in paths with the given ID.
        """

        if isinstance(plugin_id, bytes):
            plugin_id = plugin_id.decode()

        ids = self.list_ids()
        return tuple(path for path, id in ids.items() if id == plugin_id)

    @_stringify()
    def save_node(self, file_name, path=b'', /, *, with_comments=True):
        """Save the contents of the node at "path" into a file.

        The contents are saved with comments if "with_comments" is equal to
        True (the default).
        """

        save_cmd = (b'?save:' if with_comments else b'?saveshort:')

        return self._send_command(path.strip() + save_cmd + file_name + b'\n')

    @_stringify()
    def save_monitor_vars(self, file_name, path=b'', /):
        """Save the contents of all monitor variables under the node at "path".
        """

        return self._send_command(path.strip() + b'?savemons:' + file_name +
                                  b'\n')

    @_stringify()
    def read_cfg(self, file_name, path=b'', /):
        """Read the contents of "file_name" into the parser node at "path".
        """

        return self._send_command(path.strip() + b'?read:' + file_name + b'\n')

    def get_recursive(self, path='', perm=None):
        """Recursively retrieve all variables under a parser node.

        This is a Python equivalent of MATLAB's mha_get.m. If the node
        at ``path`` is a parser, it recurses into all entries and returns
        a nested dictionary. Otherwise it returns the converted leaf value.

        Parameters
        ----------
        path : str, optional
            The MHA parser path to start from. Default is the root.
        perm : str or None, optional
            If given, only include variables with this permission
            (e.g. ``'writable'``).

        Returns
        -------
        dict or value
            A nested dictionary for parser nodes, or a Python value
            for leaf variables.
        """
        node_type = self.get_type(path)

        if node_type == 'parser':
            result = {}
            entries = self.get_entries(path)
            for entry in entries:
                child_path = '{}.{}'.format(path, entry) if path else entry
                if perm is not None:
                    try:
                        if not self.is_writable(child_path):
                            if perm == 'writable':
                                continue
                    except ValueError:
                        pass
                result[entry] = self.get_recursive(child_path, perm=perm)
            return result

        return self.get_val(path)

    def set_recursive(self, path, values):
        """Recursively set MHA variables from a dictionary.

        This is a Python equivalent of MATLAB's mha_set.m. It converts
        the dictionary to a flat list of MHA assignments (using
        :func:`~openMHA.mha_utils.dict_to_mhacfg`) and sends each one.

        Parameters
        ----------
        path : str
            The MHA parser path prefix.
        values : dict or value
            A nested dictionary of values to set, or a single value.
        """
        from .mha_utils import dict_to_mhacfg

        assignments = dict_to_mhacfg(values, prefix=path)
        for assignment in assignments:
            cmd = assignment + '\n'
            if isinstance(cmd, str):
                cmd = cmd.encode('utf-8')
            self._send_command(cmd)

    def __enter__(self):
        """The enter method of the context manager protocol.
        """

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """The exit method of the context manager protocol.
        """

        self._sock.close()
        # do *not* ignore exceptions raised in the with-statement context
        return False

    def close(self):
        """Close the connection."""
        self._sock.close()
