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

"""Start and manage openMHA processes.

This module provides a Python equivalent of the MATLAB mha_start.m function.
It spawns an MHA process with automatic port selection and returns an
MHAConnection ready for use.

Example usage:
    from openMHA.mha_start import mha_start

    conn, process = mha_start()
    print(conn.get_val('fragsize'))
    conn.set_val('cmd', 'quit')
"""

import os
import shutil
import socket
import subprocess

from .MHAConnection import MHAConnection


def mha_start(port=0, extra_args=None, timeout=10):
    """Start a new MHA process and return an MHAConnection to it.

    This is a Python equivalent of MATLAB's mha_start.m. It:
    1. Opens a temporary TCP server socket on localhost
    2. Spawns the 'mha' process with --port and --announce options
    3. Waits for MHA to announce its PID and chosen port
    4. Returns an MHAConnection connected to the new MHA instance

    Parameters
    ----------
    port : int, optional
        TCP port for the MHA to listen on. 0 (default) means the OS
        will choose a free port automatically.
    extra_args : list of str, optional
        Additional command line arguments to pass to the mha binary.
    timeout : int or float, optional
        Timeout in seconds for waiting for the MHA process to start.
        Default is 10.

    Returns
    -------
    connection : MHAConnection
        A connection to the newly started MHA instance.
    process : subprocess.Popen
        The MHA subprocess object. Can be used for debugging or to
        read stdout/stderr. The process will be terminated when
        'cmd=quit' is sent via the connection.

    Raises
    ------
    FileNotFoundError
        If the 'mha' binary cannot be found.
    TimeoutError
        If the MHA process does not announce its port within the timeout.
    """
    if extra_args is None:
        extra_args = []

    binary = _find_mha_binary()

    # Open a temporary server socket to receive the MHA's port announcement
    acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    acceptor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    acceptor.bind(('127.0.0.1', 0))
    acceptor.listen(1)
    acceptor.settimeout(timeout)
    announce_port = acceptor.getsockname()[1]

    # Build command line
    cmd = [binary,
           '--port', str(port),
           '--announce', str(announce_port)]
    cmd.extend(extra_args)

    # Start the MHA process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for MHA to connect back and announce its PID and port
    try:
        conn, _addr = acceptor.accept()
    except socket.timeout:
        process.kill()
        raise TimeoutError(
            f"MHA process did not announce its port within {timeout} seconds. "
            f"Command was: {' '.join(cmd)}"
        )
    finally:
        acceptor.close()

    data = b''
    while b'\n' not in data or data.count(b'\n') < 2:
        chunk = conn.recv(1024)
        if not chunk:
            break
        data += chunk
    conn.close()

    # Parse "pid = <N>\nport = <N>\n"
    lines = data.decode().strip().splitlines()
    mha_pid = None
    mha_port = None
    for line in lines:
        if line.startswith('pid = '):
            mha_pid = int(line.split('=')[1].strip())
        elif line.startswith('port = '):
            mha_port = int(line.split('=')[1].strip())

    if mha_port is None:
        process.kill()
        raise RuntimeError(
            f"Failed to parse MHA port announcement. Received: {data!r}"
        )

    connection = MHAConnection('localhost', mha_port, timeout=timeout)
    return connection, process


def _find_mha_binary():
    """Locate the mha binary.

    Checks MHA_INSTALL_DIR environment variable first, then falls back
    to searching PATH.
    """
    install_dir = os.environ.get('MHA_INSTALL_DIR', '')
    if install_dir:
        candidate = os.path.join(install_dir, 'mha')
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    # Fall back to PATH
    mha_path = shutil.which('mha')
    if mha_path:
        return mha_path

    raise FileNotFoundError(
        "Cannot find the 'mha' binary. Set the MHA_INSTALL_DIR environment "
        "variable or ensure 'mha' is on your PATH."
    )
