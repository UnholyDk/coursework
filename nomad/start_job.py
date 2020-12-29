#!env/bin/python
import subprocess
import requests
import time
from base64 import b64decode    

URL = 'http://127.0.0.1:4646/v1'
JobID = 'fibonacci'

json_run_job = subprocess.check_output(['nomad', 'job', 'run', '-output', 'fibonacci.hcl'])
response = requests.post(URL + '/jobs', json_run_job)

response = requests.get(URL + f'/job/{JobID}/scale')

if response.json()['JobStopped'] == False:
    print(f'{JobID} stoped')
    response = requests.delete(URL + f'/job/{JobID}?purge=true')
    response = requests.post(URL + '/jobs', json_run_job)

response = requests.get(URL + '/job/fibonacci')
status_job = response.json()['Status']
time.sleep(1)
alloc_id = requests.get(URL + f'/job/{JobID}/allocations').json()[0]['ID']


print(f'Now status {JobID} job: {status_job}')

while status_job != 'dead':
    time.sleep(5)
    response = requests.get(URL + '/job/fibonacci')
    status_job = response.json()['Status']
    print(f'Now status {JobID} job: {status_job}')


params_for_get_result = {'task': JobID, 'type': 'stdout'}
response = requests.get(URL + f'/client/fs/logs/{alloc_id}', params_for_get_result)
result = b64decode(response.json()['Data']).decode().strip()
print(f'{JobID} job is complete!')
print(f'Result: {result}')
