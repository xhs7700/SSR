import json
from random import choice

if __name__ == '__main__':
	devices = {'devices': []}
	status_list = ['offline', 'online', 'malfunction']
	n = 100
	for i in range(n):
		name = f'设备 {i + 1}'
		status = choice(status_list)
		devices['devices'].append({
			'name': name,
			'status': status,
		})
	with open('./devices.json', 'w', encoding='utf-8') as fp:
		devices_str = json.dumps(devices, ensure_ascii=False, indent=2)
		fp.write(devices_str)
