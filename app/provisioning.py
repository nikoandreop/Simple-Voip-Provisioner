from dataclasses import dataclass

from .models import ProvisionRequest, ProvisionResponse, Transport, Vendor


@dataclass
class FirmwareCatalog:
    polycom: str = "4.0.16"
    yealink: str = "96.86.0.45"
    grandstream: str = "1.0.13.4"
    cisco: str = "11.3.7"


def normalize_mac(mac: str) -> str:
    cleaned = "".join(c for c in mac if c.isalnum()).upper()
    if len(cleaned) != 12:
        raise ValueError("MAC must contain 12 hex characters")
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
            f"<?xml version='1.0'?>\n"
            f"<polycom>\n"
            f"  <reg user='{req.sip_user}' pass='{req.sip_password}' server='{req.sip_server}' />\n"
            f"  <line extension='{req.extension}' />\n"
            f"</polycom>"
        )

    if req.vendor == Vendor.yealink:
        return (
            f"#!version:1.0.0.1\n"
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
        f"<device>\n"
        f"  <sipProfile>\n"
        f"    <name>{req.sip_user}</name>\n"
        f"    <authPassword>{req.sip_password}</authPassword>\n"
        f"    <proxy>{req.sip_server}</proxy>\n"
        f"  </sipProfile>\n"
        f"  <directoryNumber>{req.extension}</directoryNumber>\n"
        f"  <mac>{normalized_mac}</mac>\n"
        f"</device>"
    )


def transport_base_url(transport: Transport) -> str:
    if transport == Transport.tftp:
        return "tftp://provisioner.local"
    if transport == Transport.ftp:
        return "ftp://provisioner.local"
    return "https://provisioner.local"


def build_provisioning(req: ProvisionRequest) -> ProvisionResponse:
    mac = normalize_mac(req.mac)
    filename = vendor_filename(req.vendor, mac)
    config_body = render_config(req, mac)
    base = transport_base_url(req.transport)
    firmware_version = getattr(FirmwareCatalog(), req.vendor.value)
    firmware_url = f"{base}/firmware/{req.vendor.value}/{req.model}/{firmware_version}"
    config_url = f"{base}/configs/{req.vendor.value}/{filename}"

    return ProvisionResponse(
        mac=mac,
        vendor=req.vendor,
        model=req.model,
        config_filename=filename,
        firmware_url=firmware_url,
        config_url=config_url,
        protocol=req.transport.value,
        config_body=config_body,
    )
