import json
from hashlib import sha256

import requests

local_url = 'http://localhost:8000/users/'
remote_url = 'http://45.134.171.215:8000/users/'
internal_url = 'http://192.168.1.111:8000/users/'
register_data = {
	'username': 'xhs7700',
	'psw1': '1234567',
	'psw2': '1234567',
	'email': 'hsxia18@fudan.edu.cn',
	'auth': 'admin',
}
login_data = {
	'username': 'xhs7700',
	'psw': '1234567',
	'auth': 'consumer',
}
get_place_device_data = {
	'username': 'xhs',
	'psw': '(644000)xhs'
}

nearby_data = {
	'longitude': 121.501243,
	'latitude': 31.291311,
	'nums': 10,
}


def hash_code(s, salt='users_hash'):
	h = sha256()
	s += salt
	h.update(s.encode())
	return h.hexdigest()


def register_test(url):
	print('register_test:')
	resp = requests.post(url + 'register/', json=register_data)
	print(resp.json())


def profile_test(url):
	print('profile_test:')
	resp=requests.post(url+'login/',json=login_data)
	cookie=resp.cookies
	print(cookie.items())
	print(resp.json())
	resp=requests.post(url+'get/profile/',cookies=cookie)
	print(resp.json())
	resp=requests.post(url+'logout/',cookies=cookie)
	print(resp.json())


def login_logout_test(url):
	print('login_logout_test:')
	resp = requests.post(url + 'login/', json=login_data)
	cookie = resp.cookies
	print(cookie.items())
	print(resp.json())
	resp = requests.post(url + 'login/', json=login_data, cookies=cookie)
	print(resp.json())
	resp = requests.post(url + 'logout/', cookies=cookie)
	print(resp.json())


def nearby_test(url):
	print('nearby_test:')
	
	resp = requests.post(url + 'login/', json=login_data)
	cookie = resp.cookies
	print(cookie.items())
	print(resp.json())
	resp = requests.post(url + 'get/device/all/', json=nearby_data, cookies=cookie)
	print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
	resp = requests.post(url + 'logout/', cookies=cookie)
	print(resp.json())


def asset_test(url):
	print('asset_test:')
	resp = requests.post(url + 'login/', json=login_data)
	cookie = resp.cookies
	print(cookie.items())
	print(resp.json())
	resp = requests.post(url + 'set/asset/', json={'asset': 1000}, cookies=cookie)
	print(resp.json())
	resp = requests.post(url + 'logout/', cookies=cookie)
	print(resp.json())


def get_place_device_test(url):
	print('get_place_device_test:')
	resp = requests.post(url + 'login/', json=get_place_device_data)
	cookie = resp.cookies
	print(resp.json())
	resp = requests.post(url + 'get/place/', cookies=cookie)
	print(resp.json())
	resp = requests.post(url + 'get/device/', cookies=cookie)
	print(resp.json())
	resp = requests.post(url + 'logout/', cookies=cookie)
	print(resp.json())


if __name__ == '__main__':
	# get_place_device_test(local_url)
	# login_logout_test(local_url)
	# print(hash_code('1234567'))
	# asset_test(internal_url)
	profile_test(internal_url)