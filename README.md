# Simple VoIP Provisioner

Production-oriented VoIP phone provisioner for:

- Polycom
- Yealink
- Grandstream
- Cisco

## What it does

- API endpoint to generate per-device config from MAC + SIP details.
- Saves config files to a server folder (`PROVISIONER_CONFIGS_ROOT`).
- Checks a server firmware folder (`PROVISIONER_FIRMWARE_ROOT`) for vendor/model firmware files.
- Returns URLs for config and firmware over TFTP/FTP/HTTPS.
- Serves config and firmware folders via `/configs/*` and `/firmware/*`.

## Environment

```bash
PROVISIONER_HOST=provisioner.example.com
PROVISIONER_FIRMWARE_ROOT=/srv/voip/firmware
PROVISIONER_CONFIGS_ROOT=/srv/voip/configs
PROVISIONER_MAX_CONFIG_SIZE=65536
```

## Firmware folder layout

The provisioner checks this structure and picks the newest file by modification time:

```text
/srv/voip/firmware/
  polycom/VVX450/<firmware_file>
  yealink/T46U/<firmware_file>
  grandstream/GRP2612/<firmware_file>
  cisco/CP-8841/<firmware_file>
```

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API example

```bash
curl -X POST http://127.0.0.1:8000/api/provision \
  -H 'content-type: application/json' \
  -d '{
    "mac": "aa:bb:cc:dd:ee:ff",
    "vendor": "polycom",
    "model": "VVX450",
    "transport": "https",
    "sip_server": "sip.example.com",
    "sip_user": "1001",
    "sip_password": "supersecret",
    "extension": "1001"
  }'
```

## Health

- `GET /health`
- `GET /ready`

