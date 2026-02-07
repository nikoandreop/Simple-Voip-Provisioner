# Simple VoIP Provisioner

A starter VoIP phone provisioner for:

- Polycom
- Yealink
- Grandstream
- Cisco

It exposes:

- A Web UI at `/` to generate phone profiles
- A REST API at `POST /api/provision` to generate provisioning metadata by MAC
- Per-vendor configuration templates
- Firmware URL generation supporting `tftp`, `ftp`, and `https`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

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

## Notes

This is intentionally simple and intended as a foundation. In production, add:

- AuthN/AuthZ
- Encryption-at-rest for secrets
- Persistent storage of profiles/tenants
- Actual firmware hosting with checksum validation
- Vendor-specific config parameters beyond baseline SIP settings
