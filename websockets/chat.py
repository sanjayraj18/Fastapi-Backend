"""A normal chat participant. One terminal per person.

    uv run python chat.py lobby alice
"""

import asyncio
import sys

import websockets

PORT = 8000


async def main() -> None:
    room = sys.argv[1] if len(sys.argv) > 1 else "lobby"
    user = sys.argv[2] if len(sys.argv) > 2 else "anon"
    url = f"ws://localhost:{PORT}/ws/{room}/{user}"

    async with websockets.connect(url) as ws:
        print(f"connected as {user} in {room}. type + enter to send, ctrl-c to quit.\n")

        async def receive() -> None:
            try:
                async for msg in ws:
                    # \r rewrites the prompt line so incoming text does not
                    # get tangled up with whatever you are halfway typing
                    print(f"\r<< {msg}\n> ", end="", flush=True)
            except websockets.ConnectionClosed:
                print("\r-- connection closed by server --", flush=True)

        rx = asyncio.create_task(receive())
        try:
            while True:
                line = await asyncio.to_thread(input, "> ")
                if line.strip():
                    await ws.send(line)
        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            rx.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nbye")
