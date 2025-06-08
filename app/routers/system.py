"""System related endpoints."""

import os
import socket
import serial
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class WiFiCreds(BaseModel):
    """WiFi credentials schema."""

    ssid: str
    password: str


@router.post("/set-wifi")
async def set_wifi(creds: WiFiCreds):
    """Send WiFi credentials over serial to the device."""
    try:
        ser = serial.Serial("COMx", 115200, timeout=1)
        cmd = f"{creds.ssid},{creds.password}\n"
        ser.write(cmd.encode())
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover
        return {"error": str(exc)}


@router.get("/api/system-status")
def system_status():
    """Return basic connection information."""
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return {
            "connected": True,
            "ssid": os.getenv("WIFI_SSID", "Unknown"),
            "ip": ip,
        }
    except Exception:  # pragma: no cover
        return {"connected": False}

