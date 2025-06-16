#!/usr/bin/env python3
import asyncio
import socketio
import pandas as pd
import os
import signal
import sys
import ssl
import logging
from dotenv import load_dotenv
import aiohttp
import certifi

load_dotenv()

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

connected_terminals = []
terminals_lock = asyncio.Lock()


class TerminalSocketIOClient:
    def __init__(self, mid, tid, token):
        self.mid = mid
        self.tid = tid
        self.token = token
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=self.connector)
        self.sio = socketio.AsyncClient(
            logger=False, engineio_logger=False, http_session=self.session
        )
        self.url = f"wss://api-terminal-gateway.tillpayments.dev/socket.io/?tid={tid}&mid={mid}&token={token}"
        self.masked_url = f"wss://api-terminal-gateway.tillpayments.dev/socket.io/?tid={tid}&mid={mid}&token=***"
        self.connected = False
        self._register_handlers()

    def _register_handlers(self):
        @self.sio.event
        async def connect():
            logger.info(f"[MID:{self.mid} TID:{self.tid}] Connected to server")
            self.connected = True
            async with terminals_lock:
                if [self.mid, self.tid] not in connected_terminals:
                    connected_terminals.append([self.mid, self.tid])
                logger.info(
                    f"Connected terminals: {connected_terminals} (Total: {len(connected_terminals)})"
                )

        @self.sio.event
        async def disconnect():
            logger.info(f"[MID:{self.mid} TID:{self.tid}] Disconnected from server")
            self.connected = False
            async with terminals_lock:
                if [self.mid, self.tid] in connected_terminals:
                    connected_terminals.remove([self.mid, self.tid])
                logger.info(
                    f"Connected terminals: {connected_terminals} (Total: {len(connected_terminals)})"
                )

        @self.sio.on("*")
        async def catch_all(event, data):
            logger.info(f"[MID:{self.mid} TID:{self.tid}] Event: {event}, Data: {data}")

        @self.sio.on("message")
        async def on_message(data):
            logger.info(f"[MID:{self.mid} TID:{self.tid}] Message: {data}")

        @self.sio.event
        async def ping():
            async with terminals_lock:
                logger.info(
                    f"[MID:{self.mid} TID:{self.tid}] PING received - Connected terminals: {connected_terminals} (Total: {len(connected_terminals)})"
                )

        @self.sio.event
        async def pong():
            async with terminals_lock:
                logger.info(
                    f"[MID:{self.mid} TID:{self.tid}] PONG sent - Connected terminals: {connected_terminals} (Total: {len(connected_terminals)})"
                )

    async def connect(self):
        for attempt in range(3):
            try:
                logger.info(
                    f"[MID:{self.mid} TID:{self.tid}] Connecting to {self.masked_url} (attempt {attempt+1})..."
                )
                await self.sio.connect(self.url, transports=["websocket"])
                await self.sio.wait()
                break
            except Exception as e:
                logger.error(f"[MID:{self.mid} TID:{self.tid}] Connection error: {e}")
                await asyncio.sleep(5)
        await self.session.close()


async def run_client(mid, tid, token):
    client = TerminalSocketIOClient(mid, tid, token)
    while True:
        try:
            await client.connect()
            logger.info(f"[MID:{mid} TID:{tid}] Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"[MID:{mid} TID:{tid}] Error: {e}")
            logger.info(f"[MID:{mid} TID:{tid}] Retrying in 5 seconds...")
            await asyncio.sleep(5)


async def periodic_status():
    """Show periodic status of all connections"""
    while True:
        await asyncio.sleep(25)  # Every 25 seconds to align with server ping interval
        async with terminals_lock:
            if connected_terminals:
                logger.info(
                    f"STATUS: {len(connected_terminals)} terminals connected: {connected_terminals}"
                )
            else:
                logger.info("STATUS: No terminals connected")


async def main():
    token = os.getenv("TOKEN")
    if not token:
        logger.error("Error: TOKEN not found in .env file")
        return
    try:
        df = pd.read_csv("terminals.csv")
        terminals = df[["mid", "tid"]].to_dict("records")
    except Exception as e:
        logger.error(f"Error reading terminals.csv: {e}")
        return
    if not terminals:
        logger.error("No terminals found in CSV file")
        return
    logger.info(f"Starting Socket.IO clients for {len(terminals)} terminals...")

    def signal_handler(signum, frame):
        logger.info("\nDisconnecting all clients...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    status_task = asyncio.create_task(periodic_status())

    tasks = []
    for terminal in terminals:
        task = asyncio.create_task(run_client(terminal["mid"], terminal["tid"], token))
        tasks.append(task)
    try:
        await asyncio.gather(status_task, *tasks)
    except KeyboardInterrupt:
        logger.info("\nExiting...")
        status_task.cancel()
        for task in tasks:
            task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
