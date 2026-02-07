from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_provision_for_yealink_https():
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
    assert body['config_filename'] == 'yAABBCCDDEEFF.cfg'
    assert body['config_url'].startswith('https://')
    assert 'account.1.user_name = 1001' in body['config_body']


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
    assert '12 hex' in response.json()['detail']
