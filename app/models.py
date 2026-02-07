from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Vendor(str, Enum):
    polycom = "polycom"
    yealink = "yealink"
    grandstream = "grandstream"
    cisco = "cisco"


class Transport(str, Enum):
    tftp = "tftp"
    ftp = "ftp"
    https = "https"


class ProvisionRequest(BaseModel):
    mac: str = Field(..., description="Phone MAC address")
    vendor: Vendor
    model: str = Field(..., description="Phone model")
    transport: Transport = Transport.https
    sip_server: str
    sip_user: str
    sip_password: str
    extension: str


class ProvisionResponse(BaseModel):
    mac: str
    vendor: Vendor
    model: str
    config_filename: str
    firmware_url: str
    config_url: str
    protocol: Literal["tftp", "ftp", "https"]
    config_body: str
