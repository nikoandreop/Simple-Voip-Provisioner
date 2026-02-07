from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.settings import settings


client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_ready():
    response = client.get('/ready')
    assert response.status_code == 200
    assert response.json()['firmware_root_exists'] is True
    assert response.json()['configs_root_exists'] is True


def test_provision_firmware_found(tmp_path: Path):
    vendor_model = settings.firmware_root / 'yealink' / 'T46U'
    vendor_model.mkdir(parents=True, exist_ok=True)
    fw = vendor_model / 'firmware.rom'
    fw.write_text('dummy', encoding='utf-8')

    payload = {
        'mac': 'aa:bb:cc:dd:ee:ff',
        'vendor': 'yealink',
        'model': 'T46U',
        'transport': 'https',
        'sip_server': 'sip.example.com',
        'sip_user': '1001',
        'sip_password': 'secret',
        'extension': '1001',
    }

    response = client.post('/api/provision', json=payload)
    assert response.status_code == 200
    body = response.json()

    assert body['mac'] == 'AABBCCDDEEFF'
    assert body['firmware_found'] is True
    assert body['firmware_url'].endswith('/firmware/yealink/T46U/firmware.rom')
    assert body['config_url'].startswith('https://')


def test_provision_bad_mac_rejected():
    payload = {
        'mac': 'badmac',
        'vendor': 'polycom',
        'model': 'VVX450',
        'transport': 'tftp',
        'sip_server': 'sip.example.com',
        'sip_user': '1002',
        'sip_password': 'secret',
        'extension': '1002',
    }

    response = client.post('/api/provision', json=payload)
    assert response.status_code == 400
    assert 'hexadecimal' in response.json()['detail']
