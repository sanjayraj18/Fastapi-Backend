"""Pump enough traffic into the room to fill a wedged peer's queue.

    uv run python flood.py 1000
"""

import asyncio
import sys
import time

import websockets

PORT = 8000
SIZE = 32 * 1024


async def drain(ws) -> None:
    """We are in the room too, so we receive our own flood. Throw it away --
    otherwise this client wedges itself and proves nothing."""
    try:
        async for _ in ws:
            pass
    except websockets.ConnectionClosed:
        pass


async def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    url = f"ws://localhost:{PORT}/ws/lobby/flood"

    async with websockets.connect(url, max_queue=64) as ws:
        rx = asyncio.create_task(drain(ws))
        payload = "x" * SIZE

        print(f"sending {n} x {SIZE // 1024}KB into lobby ...")
        t0 = time.time()
        for i in range(n):
            await ws.send(f"{i} {payload}")
        elapsed = time.time() - t0

        mb = n * SIZE / 1024 / 1024
        print(f"sent {n} messages ({mb:.1f} MB) in {elapsed:.2f}s -> {n / elapsed:,.0f} msg/s")
        print("the send loop never blocked -- that is the point.")

        await asyncio.sleep(2)
        rx.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
