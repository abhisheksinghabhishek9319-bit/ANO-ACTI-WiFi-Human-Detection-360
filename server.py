import asyncio
import json
import random
import time
from collections import deque

import numpy as np
import websockets

# Config
rssi_history = deque(maxlen=20)
USE_REAL_WIFI = False  # Real wlan0 nahi hai isliye Demo Mode ON

def get_rssi_demo():
    """Real WiFi jaisa RSSI up-down simulate karega"""
    base = -38 + random.randint(-5, 5)
    return base + int(random.gauss(0, 2.5))

async def handler(websocket):
    print("[+] Browser connected - Live Radar ON")
    try:
        async for _ in range(1000000): # infinite loop ka clean way
            rssi = get_rssi_demo()
            rssi_history.append(rssi)

            # Variance calculate - hilne ka pata isse chalega
            if len(rssi_history) > 5:
                variance = float(np.var(list(rssi_history)))
                # kabhi-kabhi tez movement simulate
                if random.random() > 0.75:
                    variance += random.uniform(2, 8)
            else:
                variance = 0.0

            is_moving = variance > 2.5

            data = {
                "rssi": rssi,
                "variance": round(variance, 2),
                "is_moving": is_moving,
                "timestamp": time.time()
            }

            await websocket.send(json.dumps(data))
            await asyncio.sleep(0.25)  # 4 updates per second

    except websockets.exceptions.ConnectionClosed:
        print("[-] Browser disconnected")
    except Exception as e:
        print(f"[!] Error: {e}")

async def main():
    print("[*] Starting Live Server on ws://0.0.0.0:8765")
    print("[*] Ab browser me Live_room.html khol")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Server stopped by user")
