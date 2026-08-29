"""A genuinely stalled peer: connected, never reads.

Why this uses a raw socket instead of the websockets library: a library client
that simply never calls recv() does NOT wedge. It runs a background task that
drains the socket into memory whether you ask for messages or not, so the
network never backs up and the server never notices. Measured: such a "stalled"
client happily absorbed 19 MB.

To actually close the TCP window you have to own the socket yourself, do the
handshake by hand, and then never touch it again.

    uv run python wedge.py
"""

import base64
import fcntl
import os
import socket
import struct
import termios
import time

PORT = 8000
ROOM = "lobby"
USER = "wedged"


def handshake() -> socket.socket:
    s = socket.create_connection(("localhost", PORT))
    # A small receive buffer means the window closes after a few KB instead of
    # after the OS has quietly auto-tuned its way up to several megabytes.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4096)

    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall(
        f"GET /ws/{ROOM}/{USER} HTTP/1.1\r\n"
        f"Host: localhost:{PORT}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n\r\n".encode()
    )

    resp = s.recv(4096)          # the ONLY read this program ever performs
    if b"101" not in resp.split(b"\r\n", 1)[0]:
        raise SystemExit(f"handshake failed: {resp[:120]!r}")
    return s


def unread_bytes(s: socket.socket) -> int:
    return struct.unpack("I", fcntl.ioctl(s, termios.FIONREAD, struct.pack("I", 0)))[0]


def main() -> None:
    s = handshake()
    print(f"wedged peer connected as {USER} in {ROOM}.")
    print("reading NOTHING from here on. ctrl-c to release.\n")

    while True:
        n = unread_bytes(s)
        print(f"  unread bytes stuck in my receive buffer: {n:>8,}", flush=True)
        time.sleep(2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nwedge released")
