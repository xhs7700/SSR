import datetime
import json
from hashlib import sha256

from django.core import mail
from django.test import TestCase, Client

from users.models import User, ConfirmString, Device
from users.views import inject_places, inject_devices, inject_orders

reason_already_logout = 'Already logout.'
reason_not_post = 'Request method is not POST.'


def hash_code(s, salt='users_hash'):
	h = sha256()
	s += salt
	h.update(s.encode())
	return h.hexdigest()


def get_response(resp_dict, content):
	if content is not None:
		resp_dict['content'] = content
	resp_bytes = json.dumps(resp_dict, ensure_ascii=False).encode(encoding='utf-8')
	return resp_bytes


def get_ok_response(request_type, content=None):
	resp_dict = {
		'status': 'ok',
		'type': request_type,
	}
	return get_response(resp_dict, content)


def get_error_response(reason, content=None):
	resp_dict = {
		'status': 'error',
		'type': reason,
	}
	return get_response(resp_dict, content)


def create_user(name, psw, auth='consumer', asset=60, has_conf=True, email=None):
	if email is None:
		email = name + '@test.com'
	user = User(
		name=name,
		psw=hash_code(psw),
		email=email,
		has_confirmed=has_conf,
		asset=asset,
		auth=auth
	)
	user.save()
	return user


def login_input(name, psw, auth='consumer'):
	return {
		'username': name,
		'psw': psw,
		'auth': auth,
	}


def login_post(self, name, psw, auth='consumer'):
	data = login_input(name, psw, auth)
	return self.client.post(path='/users/login/', data=data, content_type='application/json')


def assert_wrapper_ok(self, resp, request_type, content=None):
	self.assertEqual(resp.status_code, 200)
	resp_data = get_ok_response(request_type, content)
	self.assertEqual(resp.content, resp_data)


def assert_wrapper_dict(self, resp, request_type):
	self.assertEqual(resp.status_code, 200)
	resp_dict = json.loads(str(resp.content, encoding='utf-8'))
	self.assertEqual(resp_dict['status'], 'ok')
	self.assertEqual(resp_dict['type'], request_type)


def assert_wrapper_error(self, resp, reason):
	self.assertEqual(resp.status_code, 200)
	resp_data = get_error_response(reason)
	self.assertEqual(resp.content, resp_data)


class LoginTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw')
		create_user('test2', 'testpsw', has_conf=False)
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
	
	def test_re_login(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = login_post(self, 'test1', 'testpsw')
		assert_wrapper_error(self, resp, 'Already login.')
	
	def test_get_method(self):
		data = login_input('test1', 'testpsw')
		resp = self.client.get('/users/login/', data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_not_confirmed(self):
		resp = login_post(self, 'test2', 'testpsw')
		assert_wrapper_error(self, resp, 'User has not accomplished email confirmation.')
	
	def test_user_not_exist(self):
		resp = login_post(self, 'test', 'testpsw')
		assert_wrapper_error(self, resp, 'Username not exist.')
	
	def test_wrong_psw(self):
		resp = login_post(self, 'test1', 'wrongpsw')
		assert_wrapper_error(self, resp, 'Wrong password.')
	
	def test_wrong_auth(self):
		resp = login_post(self, 'test1', 'testpsw', 'business')
		assert_wrapper_error(self, resp, 'Invalid Authority.')


def reg_input(name, psw1, psw2=None, email=None, auth='consumer'):
	if psw2 is None:
		psw2 = psw1
	if email is None:
		email = name + '@test.com'
	return {
		'username': name,
		'psw1': psw1,
		'psw2': psw2,
		'email': email,
		'auth': auth,
	}


def reg_post(self, name, psw1, psw2=None, email=None, auth='consumer'):
	data = reg_input(name, psw1, psw2, email, auth)
	return self.client.post(path='/users/register/', data=data, content_type='application/json')


class RegisterTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw', email='test@test.com')
		self.client = Client()
	
	def test_normal(self):
		name, email_addr = 'test', 'test@correct.com'
		resp = reg_post(self, name, 'testpsw', email=email_addr)
		assert_wrapper_ok(self, resp, 'register')
		email = mail.outbox[0]
		self.assertEqual(email.from_email, 'covid19_mailapi@qq.com')
		self.assertEqual(email.to, [email_addr])
		self.assertEqual(email.subject, f'Registration Confirm: {name}')
	
	def test_already_login(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = reg_post(self, 'test', 'testpsw')
		assert_wrapper_error(self, resp, 'Already login.')
	
	def test_get_method(self):
		data = reg_input('test', 'testpsw')
		resp = self.client.get(path='/users/register/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_null_username(self):
		resp = reg_post(self, '', 'testpsw', email='test@test.com')
		assert_wrapper_error(self, resp, 'Username cannot be null.')
	
	def test_invalid_email(self):
		resp = reg_post(self, 'test', 'testpsw', email='test')
		assert_wrapper_error(self, resp, 'Invalid email address.')
	
	def test_invalid_auth(self):
		resp = reg_post(self, 'test', 'testpsw', auth='user')
		assert_wrapper_error(self, resp, 'Invalid authority.')
	
	def test_psw_not_match(self):
		resp = reg_post(self, 'test', 'testpsw', psw2='testps',email='xhstest@test.com')
		assert_wrapper_error(self, resp, 'Two password input do not match.')
	
	def test_null_psw(self):
		resp = reg_post(self, 'test', '')
		assert_wrapper_error(self, resp, 'Password cannot be null.')
	
	def test_exist_username(self):
		resp = reg_post(self, 'test1', 'testpsw')
		assert_wrapper_error(self, resp, 'Username already exist.')
	
	def test_exist_email(self):
		resp = reg_post(self, 'test', 'testpsw', email='test@test.com')
		assert_wrapper_error(self, resp, 'Email address has been used.')


def logout_post(self):
	return self.client.post(path='/users/logout/')


class LogoutTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw')
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = logout_post(self)
		assert_wrapper_ok(self, resp, 'logout')
	
	def test_already_logout(self):
		resp = logout_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)


def get_user_post(self):
	return self.client.post(path='/users/get/user/')


def login_wrapper(self, name, psw, auth='consumer'):
	resp = login_post(self, name, psw, auth)
	assert_wrapper_ok(self, resp, 'login', {'authority': auth})


class GetUserTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw')
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = get_user_post(self)
		assert_wrapper_ok(self, resp, 'get_user', {'username': 'test1'})
	
	def test_already_logout(self):
		resp = get_user_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)


def change_psw_input(old_psw, new_psw):
	return {
		'old_password': old_psw,
		'new_password': new_psw,
	}


def change_psw_post(self, old_psw, new_psw):
	data = change_psw_input(old_psw, new_psw)
	return self.client.post(path='/users/set/psw/', data=data, content_type='application/json')


class ChangePswTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw')
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = change_psw_post(self, 'testpsw', 'newpsw')
		assert_wrapper_ok(self, resp, 'change_password')
	
	def test_already_logout(self):
		resp = change_psw_post(self, 'testpsw', 'newpsw')
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'test1', 'testpsw')
		data = change_psw_input('testpsw', 'newpsw')
		resp = self.client.get(path='/users/set/psw/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_invalid_new_psw(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = change_psw_post(self, 'testpsw', '')
		assert_wrapper_error(self, resp, 'Invalid new password.')
	
	def test_same_psw(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = change_psw_post(self, 'testpsw', 'testpsw')
		assert_wrapper_error(self, resp, 'New password cannot be the same with old password.')
	
	def test_wrong_psw(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = change_psw_post(self, 'testps', 'newpsw')
		assert_wrapper_error(self, resp, 'Wrong password.')


def reset_psw_input(name, auth):
	return {'username': name, 'auth': auth}


def reset_psw_post(self, name, auth):
	data = reset_psw_input(name, auth)
	return self.client.post(path='/users/reset/psw/', data=data, content_type='application/json')


class ResetPswTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw')
		create_user('test2', 'testpsw', has_conf=False)
		self.client = Client()
	
	def test_normal(self):
		resp = reset_psw_post(self, 'test1', 'consumer')
		assert_wrapper_ok(self, resp, 'reset_password')
		email = mail.outbox[0]
		self.assertEqual(email.from_email, 'covid19_mailapi@qq.com')
		self.assertEqual(email.to, ['test1@test.com'])
		self.assertEqual(email.subject, 'Reset Password: test1')
	
	def test_already_login(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = reset_psw_post(self, 'test1', 'consumer')
		assert_wrapper_error(self, resp, 'Already login.')
	
	def test_get_method(self):
		data = reset_psw_input('test1', 'consumer')
		resp = self.client.get(path='/users/reset/psw/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_username_not_exist(self):
		resp = reset_psw_post(self, 'test', 'consumer')
		assert_wrapper_error(self, resp, 'Username not exist.')
	
	def test_not_confirm(self):
		resp = reset_psw_post(self, 'test2', 'consumer')
		assert_wrapper_error(self, resp, 'This account has not accomplished email confirmation.')
	
	def test_invalid_auth(self):
		resp = reset_psw_post(self, 'test1', 'business')
		assert_wrapper_error(self, resp, 'Invalid authority.')


def get_single_device_input(id):
	return {'id': id}


def get_single_device_post(self, id):
	data = get_single_device_input(id)
	return self.client.post(path='/users/get/device/single/', data=data, content_type='application/json')


class GetSingleDeviceTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', auth='business')
		inject_places()
		inject_devices()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = get_single_device_post(self, 1)
		assert_wrapper_dict(self, resp, 'get_device_single')
	
	def test_id_not_exist(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = get_single_device_post(self, -1)
		assert_wrapper_error(self, resp, 'Device ID not exist.')
	
	def test_already_logout(self):
		resp = get_single_device_post(self, 1)
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		data = get_single_device_input(1)
		resp = self.client.get(path='/users/get/device/single/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)


def get_all_device_input(nums=5, longitude=120.1, latitude=30.1):
	return {
		'nums': nums,
		'longitude': longitude,
		'latitude': latitude,
	}


def get_all_device_post(self, nums=5, longitude=120.1, latitude=30.1):
	data = get_all_device_input(nums, longitude, latitude)
	return self.client.post(path='/users/get/device/all/', data=data, content_type='application/json')


class GetAllDeviceTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', 'business')
		create_user('test1', 'testpsw')
		inject_places()
		inject_devices()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = get_all_device_post(self, 5, 120.1, 30.1)
		assert_wrapper_dict(self, resp, 'get_device_all')
	
	def test_already_logout(self):
		resp = get_all_device_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'test1', 'testpsw')
		data = get_all_device_input()
		resp = self.client.get(path='/users/get/device/all/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)


def get_user_place_post(self):
	return self.client.post(path='/users/get/place/', content_type='application/json')


class GetUserPlaceTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', 'business')
		inject_places()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = get_user_place_post(self)
		assert_wrapper_dict(self, resp, 'get_place')
		resp = self.client.get(path='/users/get/place/')
		assert_wrapper_dict(self, resp, 'get_place')
	
	def test_already_logout(self):
		resp = get_user_place_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
		resp = self.client.get(path='/users/get/place/')
		assert_wrapper_error(self, resp, reason_already_logout)


def add_user_place_input(name, lon=120.1, lat=30.1):
	return {
		'name': name,
		'longitude': lon,
		'latitude': lat,
	}


def add_user_place_post(self, name, lon=120.1, lat=30.1):
	data = add_user_place_input(name, lon, lat)
	return self.client.post(path='/users/add/place/', data=data, content_type='application/json')


class AddUserPlaceTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', 'business')
		inject_places()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = add_user_place_post(self, 'test place', 120.1, 30.1)
		assert_wrapper_ok(self, resp, 'add_place')
	
	def test_invalid_lon_lat(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = add_user_place_post(self, 'test place', lon=-0.1)
		assert_wrapper_error(self, resp, 'Invalid longitude/latitude.')
		resp = add_user_place_post(self, 'test place', lon=180.1)
		assert_wrapper_error(self, resp, 'Invalid longitude/latitude.')
		resp = add_user_place_post(self, 'test place', lat=-0.1)
		assert_wrapper_error(self, resp, 'Invalid longitude/latitude.')
		resp = add_user_place_post(self, 'test place', lat=90.1)
		assert_wrapper_error(self, resp, 'Invalid longitude/latitude.')
	
	def test_place_already_exist(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = add_user_place_post(self, '地点 1')
		assert_wrapper_error(self, resp, 'Place name already exist.')
	
	def test_already_logout(self):
		resp = add_user_place_post(self, 'test place')
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		data = add_user_place_input('test place')
		resp = self.client.get(path='/users/add/place/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)


def delete_user_place_input(name):
	return {'name': name}


def delete_user_place_post(self, name):
	data = delete_user_place_input(name)
	return self.client.post(path='/users/delete/place/', data=data, content_type='application/json')


class DeleteUserPlaceTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', 'business')
		inject_places()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = delete_user_place_post(self, '地点 1')
		assert_wrapper_ok(self, resp, 'delete_place')
	
	def test_already_logout(self):
		resp = delete_user_place_post(self, '地点 1')
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		data = delete_user_place_input('地点 1')
		resp = self.client.get(path='/users/delete/place/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_place_not_exist(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = delete_user_place_post(self, 'test place')
		assert_wrapper_error(self, resp, 'Place not exist.')


def get_user_device_post(self):
	return self.client.post(path='/users/get/device/', content_type='application/json')


def get_user_device_get(self):
	return self.client.get(path='/users/get/device/')


class GetUserDeviceTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', 'business')
		inject_places()
		inject_devices()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = get_user_device_post(self)
		assert_wrapper_dict(self, resp, 'get_device')
		resp = get_user_device_get(self)
		assert_wrapper_dict(self, resp, 'get_device')
	
	def test_already_logout(self):
		resp = get_user_device_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
		resp = get_user_device_get(self)
		assert_wrapper_error(self, resp, reason_already_logout)


def set_user_device_input(loc_name_old, dev_name_old, loc_name_new='地点 1', dev_name_new='设备 200', status='在线'):
	return {
		'loc_name_old': loc_name_old,
		'dev_name_old': dev_name_old,
		'loc_name': loc_name_new,
		'dev_name': dev_name_new,
		'status': status,
	}


def set_user_device_post(self, loc_name_old, dev_name_old, loc_name_new='地点 1', dev_name_new='设备 200', status='在线'):
	data = set_user_device_input(loc_name_old, dev_name_old, loc_name_new, dev_name_new, status)
	return self.client.post(path='/users/set/device/', data=data, content_type='application/json')


class SetUserDeviceTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', 'business')
		inject_places()
		inject_devices()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		device = Device.objects.get(name='设备 1')
		resp = set_user_device_post(self, device.location.name, device.name, '地点 1', '设备 200', '在线')
		assert_wrapper_ok(self, resp, 'set_device')
	
	def test_already_logout(self):
		device = Device.objects.get(name='设备 1')
		resp = set_user_device_post(self, device.location.name, device.name)
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		device = Device.objects.get(name='设备 1')
		data = set_user_device_input(device.location.name, device.name)
		resp = self.client.get(path='/users/set/device/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_invalid_status(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		device = Device.objects.get(name='设备 1')
		resp = set_user_device_post(self, device.location.name, device.name, status='online')
		assert_wrapper_error(self, resp, 'Invalid status.')
	
	def test_place_not_exist(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = set_user_device_post(self, '地点 100', '设备 1')
		assert_wrapper_error(self, resp, 'Place not exist.')
	
	def test_device_not_exist(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = set_user_device_post(self, '地点 1', '设备 200')
		assert_wrapper_error(self, resp, 'Device not exist.')


def add_user_device_input(loc_name='地点 1', dev_name='设备 200', status='在线'):
	return {
		'loc_name': loc_name,
		'dev_name': dev_name,
		'status': status,
	}


def add_user_device_post(self, loc_name='地点 1', dev_name='设备 200', status='在线'):
	data = add_user_device_input(loc_name, dev_name, status)
	return self.client.post(path='/users/add/device/', data=data, content_type='application/json')


class AddUserDeviceTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', 'business')
		inject_places()
		inject_devices()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = add_user_device_post(self, '地点 1', '设备 200', '在线')
		assert_wrapper_ok(self, resp, 'add_device')
	
	def test_already_logout(self):
		resp = add_user_device_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		data = add_user_device_input()
		resp = self.client.get(path='/users/add/device/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_device_already_exist(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		device = Device.objects.get(name='设备 1')
		resp = add_user_device_post(self, loc_name=device.location.name, dev_name=device.name)
		assert_wrapper_error(self, resp, 'Device name already exist.')
	
	def test_invalid_status(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = add_user_device_post(self, status='online')
		assert_wrapper_error(self, resp, 'Invalid status.')


def delete_user_device_input(loc_name, dev_name):
	return {
		'loc_name': loc_name,
		'dev_name': dev_name,
	}


def delete_user_device_post(self, loc_name, dev_name):
	data = delete_user_device_input(loc_name, dev_name)
	return self.client.post(path='/users/delete/device/', data=data, content_type='application/json')


class DeleteDeviceTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', 'business')
		inject_places()
		inject_devices()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		device = Device.objects.get(name='设备 1')
		resp = delete_user_device_post(self, device.location.name, device.name)
		assert_wrapper_ok(self, resp, 'delete_device')
	
	def test_already_logout(self):
		device = Device.objects.get(name='设备 1')
		resp = delete_user_device_post(self, device.location.name, device.name)
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		device = Device.objects.get(name='设备 1')
		data = delete_user_device_input(device.location.name, device.name)
		resp = self.client.get(path='/users/delete/device/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_place_not_exist(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = delete_user_device_post(self, '地点 100', '设备 1')
		assert_wrapper_error(self, resp, 'Place not exist.')
	
	def test_device_not_exist(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = delete_user_device_post(self, '地点 1', '设备 200')
		assert_wrapper_error(self, resp, 'Device not exist.')


def add_order_input(order_type='其他原因', description='lorem ipsum', device_id=1):
	return {
		'order_type': order_type,
		'description': description,
		'id': device_id,
	}


def add_order_post(self, order_type='其他原因', description='lorem ipsum', device_id=1):
	data = add_order_input(order_type, description, device_id)
	return self.client.post(path='/users/add/order/', data=data, content_type='application/json')


class AddOrderTest(TestCase):
	def setUp(self) -> None:
		for i in range(10):
			create_user(f'consumer {i + 1}', 'testpsw')
		create_user('xhs', 'testpsw', 'business')
		create_user('test1', 'testpsw')
		inject_places()
		inject_devices()
		inject_orders()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = add_order_post(self, '其他原因', 'lorem ipsum', 1)
		assert_wrapper_ok(self, resp, 'add_order')
	
	def test_already_logout(self):
		resp = add_order_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'test1', 'testpsw')
		data = add_order_input()
		resp = self.client.get(path='/users/add/order/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_invalid_order_type(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = add_order_post(self, order_type='other')
		assert_wrapper_error(self, resp, 'Invalid order type.')
	
	def test_invalid_device_id(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = add_order_post(self, device_id=-1)
		assert_wrapper_error(self, resp, 'Invalid device ID.')


def get_order_post(self):
	return self.client.post(path='/users/get/order/', content_type='application/json')


def get_order_get(self):
	return self.client.get(path='/users/get/order/')


class GetOrderTest(TestCase):
	def setUp(self) -> None:
		for i in range(10):
			create_user(f'consumer {i + 1}', 'testpsw')
		create_user('xhs', 'testpsw', 'business')
		inject_places()
		inject_devices()
		inject_orders()
		self.client = Client()
	
	def test_normal(self):
		login_wrapper(self, 'xhs', 'testpsw', 'business')
		resp = get_order_post(self)
		assert_wrapper_dict(self, resp, 'get_order')
		resp = get_order_get(self)
		assert_wrapper_dict(self, resp, 'get_order')
	
	def test_already_logout(self):
		resp = get_order_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
		resp = get_order_get(self)
		assert_wrapper_error(self, resp, reason_already_logout)


def get_asset_post(self):
	return self.client.post(path='/users/get/asset/', content_type='application/json')


def get_asset_get(self):
	return self.client.get(path='/users/get/asset/')


class GetAssetTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw')
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = get_asset_post(self)
		assert_wrapper_dict(self, resp, 'get_asset')
		resp = get_asset_get(self)
		assert_wrapper_dict(self, resp, 'get_asset')
	
	def test_already_logout(self):
		resp = get_asset_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
		resp = get_asset_get(self)
		assert_wrapper_error(self, resp, reason_already_logout)


def set_asset_input(asset=120):
	return {'asset': asset}


def set_asset_post(self, asset=120):
	data = set_asset_input(asset)
	return self.client.post(path='/users/set/asset/', data=data, content_type='application/json')


class SetAssetTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw')
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = set_asset_post(self, 120)
		assert_wrapper_ok(self, resp, 'set_asset')
	
	def test_already_logout(self):
		resp = set_asset_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'test1', 'testpsw')
		data = set_asset_input()
		resp = self.client.get(path='/users/set/asset/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)


def get_deal_post(self):
	return self.client.post(path='/users/get/deal/', content_type='application/json')


def get_deal_get(self):
	return self.client.get(path='/users/get/deal/')


class GetDealTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw')
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = get_deal_post(self)
		assert_wrapper_dict(self, resp, 'get_deal')
		resp = get_deal_get(self)
		assert_wrapper_dict(self, resp, 'get_deal')
	
	def test_already_logout(self):
		resp = get_deal_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
		resp = get_deal_get(self)
		assert_wrapper_error(self, resp, reason_already_logout)


def get_millisecond(year, month, day, hour=0):
	return int(datetime.datetime(year, month, day, hour).timestamp() * 1000)


def add_deal_input(device_id=1, start_time=get_millisecond(2020, 1, 23, 10), end_time=get_millisecond(2020, 4, 8)):
	return {
		'id': device_id,
		'start_time': start_time,
		'end_time': end_time,
	}


def add_deal_post(self, device_id=1, start_time=get_millisecond(2020, 1, 23, 10), end_time=get_millisecond(2020, 4, 8)):
	data = add_deal_input(device_id, start_time, end_time)
	return self.client.post(path='/users/add/deal/', data=data, content_type='application/json')


class AddDealTest(TestCase):
	def setUp(self) -> None:
		create_user('xhs', 'testpsw', 'business')
		create_user('test1', 'testpsw')
		inject_places()
		inject_devices()
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		start_time = get_millisecond(2020, 1, 23, 10)
		end_time = get_millisecond(2020, 4, 8)
		resp = add_deal_post(self, 1, start_time, end_time)
		assert_wrapper_ok(self, resp, 'add_deal')
	
	def test_already_logout(self):
		resp = add_deal_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
	
	def test_get_method(self):
		login_wrapper(self, 'test1', 'testpsw')
		data = add_deal_input()
		resp = self.client.get(path='/users/add/deal/', data=data)
		assert_wrapper_error(self, resp, reason_not_post)
	
	def test_invalid_device_id(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = add_deal_post(self, device_id=-1)
		assert_wrapper_error(self, resp, 'Invalid device ID.')


def get_profile_post(self):
	return self.client.post(path='/users/get/profile/', content_type='application/json')


def get_profile_get(self):
	return self.client.get(path='/users/get/profile/')


class GetProfileTest(TestCase):
	def setUp(self) -> None:
		create_user('test1', 'testpsw')
	
	def test_normal(self):
		login_wrapper(self, 'test1', 'testpsw')
		resp = get_profile_post(self)
		assert_wrapper_dict(self, resp, 'get_user_profile')
		resp = get_profile_get(self)
		assert_wrapper_dict(self, resp, 'get_user_profile')
	
	def test_already_logout(self):
		resp = get_profile_post(self)
		assert_wrapper_error(self, resp, reason_already_logout)
		resp = get_profile_get(self)
		assert_wrapper_error(self, resp, reason_already_logout)
