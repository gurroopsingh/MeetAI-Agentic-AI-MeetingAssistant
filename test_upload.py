import requests
import time

res = requests.post('http://localhost:8000/api/meetings/upload', files={'file': ('sample.mp4', open('sample.mp4', 'rb'), 'video/mp4')})
print('Upload response:', res.status_code, res.json())
meeting_id = res.json()['id']
status = res.json()['status']

while status != 'ready' and status != 'failed':
    time.sleep(1)
    status_res = requests.get(f'http://localhost:8000/api/meetings/{meeting_id}')
    status = status_res.json()['status']
    print('Current status:', status)

print('Meeting details:', requests.get(f'http://localhost:8000/api/meetings/{meeting_id}').json())

vid_res = requests.get(f'http://localhost:8000/api/meetings/{meeting_id}/video', headers={'Range': 'bytes=0-100'})
print('Video endpoint status:', vid_res.status_code)
print('Video endpoint headers:', vid_res.headers)
