import requests

URL = 'http://127.0.0.1:4646/v1'


def test_start_cluster():
    response = requests.get(URL + '/agent/members')
    assert response.status_code == 200

    for server in response.json()['Members']:
        server['Status'] == 'alive'

    response = requests.get(URL + '/nodes')
    assert response.status_code == 200

    for node in response.json():
        assert node['Status'] == 'ready'
