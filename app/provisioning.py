from pathlib import Path
import re

from .models import ProvisionRequest, ProvisionResponse, Transport, Vendor
from .settings import settings


HEX_MAC_RE = re.compile(r"^[0-9A-F]{12}$")


def normalize_mac(mac: str) -> str:
    cleaned = "".join(c for c in mac if c.isalnum()).upper()
    if not HEX_MAC_RE.match(cleaned):
        raise ValueError("MAC must contain exactly 12 hexadecimal characters")
    return cleaned


def vendor_filename(vendor: Vendor, mac: str) -> str:
    if vendor == Vendor.polycom:
        return f"{mac}-phone.cfg"
    if vendor == Vendor.yealink:
        return f"y{mac}.cfg"
    if vendor == Vendor.grandstream:
        return f"cfg{mac}"
    return f"SEP{mac}.cnf.xml"


def render_config(req: ProvisionRequest, normalized_mac: str) -> str:
    if req.vendor == Vendor.polycom:
        return (
            "<?xml version='1.0'?>\n"
            "<polycom>\n"
            f"  <reg user='{req.sip_user}' pass='{req.sip_password}' server='{req.sip_server}' />\n"
            f"  <line extension='{req.extension}' />\n"
            "</polycom>"
        )

    if req.vendor == Vendor.yealink:
        return (
            "#!version:1.0.0.1\n"
            f"account.1.label = {req.extension}\n"
            f"account.1.display_name = {req.sip_user}\n"
            f"account.1.user_name = {req.sip_user}\n"
            f"account.1.password = {req.sip_password}\n"
            f"account.1.sip_server.1.address = {req.sip_server}\n"
        )

    if req.vendor == Vendor.grandstream:
        return (
            f"P271={req.sip_server}\n"
            f"P47={req.sip_user}\n"
            f"P35={req.sip_password}\n"
            f"P270={req.extension}\n"
        )

    return (
        "<device>\n"
        "  <sipProfile>\n"
        f"    <name>{req.sip_user}</name>\n"
        f"    <authPassword>{req.sip_password}</authPassword>\n"
        f"    <proxy>{req.sip_server}</proxy>\n"
        "  </sipProfile>\n"
        f"  <directoryNumber>{req.extension}</directoryNumber>\n"
        f"  <mac>{normalized_mac}</mac>\n"
        "</device>"
    )


def transport_base_url(transport: Transport) -> str:
    if transport == Transport.tftp:
        return f"tftp://{settings.host}"
    if transport == Transport.ftp:
        return f"ftp://{settings.host}"
    return f"https://{settings.host}"


def find_firmware_file(vendor: Vendor, model: str) -> Path | None:
    model_dir = settings.firmware_root / vendor.value / model
    if not model_dir.exists() or not model_dir.is_dir():
        return None

    candidates = [p for p in model_dir.iterdir() if p.is_file()]
    if not candidates:
        return None

    # Most recently modified firmware wins.
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def save_config(vendor: Vendor, filename: str, body: str) -> Path:
    if len(body.encode("utf-8")) > settings.max_config_size_bytes:
        raise ValueError("Config exceeds max allowed size")

    target_dir = settings.configs_root / vendor.value
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / filename
    target_file.write_text(body, encoding="utf-8")
    return target_file


def build_provisioning(req: ProvisionRequest) -> ProvisionResponse:
    mac = normalize_mac(req.mac)
    filename = vendor_filename(req.vendor, mac)
    config_body = render_config(req, mac)

    saved = save_config(req.vendor, filename, config_body)
    base = transport_base_url(req.transport)
    config_url = f"{base}/configs/{req.vendor.value}/{saved.name}"

    firmware_file = find_firmware_file(req.vendor, req.model)
    firmware_url = (
        f"{base}/firmware/{req.vendor.value}/{req.model}/{firmware_file.name}"
        if firmware_file
        else None
    )

    return ProvisionResponse(
        mac=mac,
        vendor=req.vendor,
        model=req.model,
        config_filename=filename,
        firmware_url=firmware_url,
        config_url=config_url,
        protocol=req.transport.value,
        config_saved=True,
        firmware_found=firmware_file is not None,
    )
