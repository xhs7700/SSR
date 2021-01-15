import datetime
import json
import math
import sys
from functools import cmp_to_key
from hashlib import sha256
from random import choice

import pytz
import validators
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from SSR_backend import settings
from users import models
from users.models import User, ConfirmString, Place, Device, Order, Deal


def hash_code(s, salt='users_hash'):
	h = sha256()
	s += salt
	h.update(s.encode())
	return h.hexdigest()


def get_response(resp_dict, content):
	if content is not None:
		resp_dict['content'] = content
	resp_bytes = json.dumps(resp_dict, ensure_ascii=False).encode(encoding='utf-8')
	return HttpResponse(resp_bytes)


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


def make_confirm_string(user):
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	code = hash_code(user.name, now)
	models.ConfirmString.objects.create(code=code, user=user, )
	return code


def check_cookie_post(request):
	if 'is_login' not in request.session:
		reason = 'Already logout.'
		return reason
	if request.method != 'POST':
		reason = 'Request method is not POST.'
		return reason
	return 'ok'


@csrf_exempt
def login(request):
	if 'is_login' in request.session:
		reason = 'Already login.'
		return get_error_response(reason)
	if request.method != 'POST':
		reason = 'Request method is not POST.'
		return get_error_response(reason)
	request_data = json.loads(request.body)
	username, psw = request_data['username'], request_data['psw']
	auth = request_data['auth']
	try:
		user = User.objects.get(name=username)
	except:
		reason = 'Username not exist.'
		return get_error_response(reason)
	if not user.has_confirmed:
		reason = 'User has not accomplished email confirmation.'
		return get_error_response(reason)
	if user.psw != hash_code(psw):
		reason = 'Wrong password.'
		return get_error_response(reason)
	if user.auth != auth:
		reason = 'Invalid Authority.'
		return get_error_response(reason)
	request.session['is_login'] = True
	request.session['user_id'] = user.id
	request.session['user_name'] = user.name
	return get_ok_response('login', {'authority': user.auth})


@csrf_exempt
def register(request):
	request.session.clear_expired()
	if 'is_login' in request.session:
		reason = 'Already login.'
		return get_error_response(reason)
	if request.method != 'POST':
		reason = 'Request method is not POST.'
		return get_error_response(reason)
	request_data = json.loads(request.body)
	username, psw1, psw2 = request_data['username'], request_data['psw1'], request_data['psw2']
	email, auth = request_data['email'], request_data['auth']
	if username in {'', None}:
		reason = 'Username cannot be null.'
		return get_error_response(reason)
	if not validators.email(email):
		reason = 'Invalid email address.'
		return get_error_response(reason)
	if auth not in {'consumer', 'business', 'admin'}:
		reason = 'Invalid authority.'
		return get_error_response(reason)
	if psw1 != psw2:
		reason = 'Two password input do not match.'
		return get_error_response(reason)
	if psw1 == '':
		reason = 'Password cannot be null.'
		return get_error_response(reason)
	same_name_user = User.objects.filter(name=username)
	if same_name_user:
		reason = 'Username already exist.'
		return get_error_response(reason)
	same_email_user = User.objects.filter(email=email)
	if same_email_user:
		reason = 'Email address has been used.'
		return get_error_response(reason)
	new_user = User.objects.create(
		name=username,
		psw=hash_code(psw1),
		email=email,
		auth=auth,
	)
	confirm_code = make_confirm_string(new_user)
	send_register_email(email, username, confirm_code)
	return get_ok_response('register')


@csrf_exempt
def logout(request):
	if 'is_login' not in request.session:
		reason = 'Already logout.'
		return get_error_response(reason)
	request.session.flush()
	return get_ok_response('logout')


def user_confirm(request):
	confirm_code = request.GET.get('code', None)
	try:
		confirm = ConfirmString.objects.get(code=confirm_code)
	except:
		message = 'Invalid confirm request.'
		return render(request, 'users/confirm.html', locals())
	
	created_time = confirm.created_time
	now = datetime.datetime.now()
	now = now.replace(tzinfo=pytz.timezone('UTC'))
	cmp = created_time + datetime.timedelta(days=settings.CONFIRM_DAYS)
	if now > cmp:
		confirm.user.delete()
		message = 'Your email expired. Please register again.'
		return render(request, 'users/confirm.html', locals())
	confirm.user.has_confirmed = True
	confirm.user.save()
	confirm.delete()
	message = 'Successfully confirmed.'
	return render(request, 'users/confirm.html', locals())


@csrf_exempt
def get_current_user(request):
	if 'is_login' not in request.session:
		reason = 'Already logout.'
		return get_error_response(reason)
	return get_ok_response('get_user', {'username': request.session['user_name']})


@csrf_exempt
def change_password(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	request_data = json.loads(request.body)
	username = request.session['user_name']
	old_psw, new_psw = request_data['old_password'], request_data['new_password']
	if new_psw == '':
		reason = 'Invalid new password.'
		return get_error_response(reason)
	if new_psw == old_psw:
		reason = 'New password cannot be the same with old password.'
		return get_error_response(reason)
	user = User.objects.get(name=username)
	if user.psw != hash_code(old_psw):
		reason = 'Wrong password.'
		return get_error_response(reason)
	user.psw = hash_code(new_psw)
	user.save()
	return get_ok_response('change_password')


@csrf_exempt
def reset_password(request):
	if 'is_login' in request.session:
		reason = 'Already login.'
		return get_error_response(reason)
	if request.method != 'POST':
		reason = 'Request method is not POST.'
		return get_error_response(reason)
	request_data = json.loads(request.body)
	username = request_data['username']
	auth = request_data['auth']
	try:
		user = User.objects.get(name=username)
	except:
		reason = 'Username not exist.'
		return get_error_response(reason)
	if not user.has_confirmed:
		reason = 'This account has not accomplished email confirmation.'
		return get_error_response(reason)
	if user.auth != auth:
		reason = 'Invalid authority.'
		return get_error_response(reason)
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	new_psw = hash_code(username, now)[:16]
	send_reset_email(user.email, username, new_psw)
	user.psw = hash_code(new_psw)
	user.save()
	return get_ok_response('reset_password')


def get_nearby_places(lon, lat, nums):
	def dist(lon1, lat1, lon2, lat2):
		radius = 6371.004
		pi = math.pi
		lon1 *= pi / 180.0
		lat1 *= pi / 180.0
		lon2 *= pi / 180.0
		lat2 *= pi / 180.0
		tmp = math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)
		return radius * math.acos(tmp)
	
	place_set = Place.objects.all()
	place_size = len(place_set)
	nums = max(1, nums)
	nums = min(place_size, nums)
	idx = [i for i in range(place_size)]
	
	def cmp(x, y):
		lon_x, lat_x = place_set[x].longitude, place_set[y].latitude
		lon_y, lat_y = place_set[y].longitude, place_set[y].latitude
		dist1 = dist(lon_x, lat_x, lon, lat)
		dist2 = dist(lon_y, lat_y, lon, lat)
		if math.isclose(dist1, dist2):
			return 0
		return -1 if dist1 < dist2 else 1
	
	idx.sort(key=cmp_to_key(cmp))
	return [place_set[idx[i]] for i in range(nums)]


@csrf_exempt
def get_single_device(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	request_data = json.loads(request.body)
	id = request_data['id']
	try:
		device = Device.objects.get(pk=id)
	except:
		reason='Device ID not exist.'
		return get_error_response(reason)
	translate = {
		'online': '在线',
		'offline': '离线',
		'malfunction': '故障',
	}
	content = [{
		'name': device.name,
		'status': translate[device.status],
		'id': device.id,
		'location': device.location.name,
	}]
	return get_ok_response('get_device_single', content)


@csrf_exempt
def get_all_devices(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	request_data = json.loads(request.body)
	nums = int(request_data['nums'])
	lon = request_data['longitude']
	lat = request_data['latitude']
	place_set = get_nearby_places(lon, lat, nums)
	content = []
	translate = {
		'online': '在线',
		'offline': '离线',
		'malfunction': '故障',
	}
	for place in place_set:
		device_set = Device.objects.filter(location__id=place.id)
		place_content = []
		for device in device_set:
			place_content.append({
				'id': device.id,
				'name': device.name,
				'status': translate[device.status],
			})
		content.append({
			'id': place.id,
			'name': place.name,
			'latitude': place.latitude,
			'longitude': place.longitude,
			'device': place_content,
		})
	return get_ok_response('get_device_all', content)


@csrf_exempt
def get_user_places(request):
	if 'is_login' not in request.session:
		reason = 'Already logout.'
		return get_error_response(reason)
	username = request.session['user_name']
	place_set = Place.objects.filter(user__name=username)
	content = []
	for place in place_set:
		content.append({
			'name': place.name,
			'latitude': place.latitude,
			'longitude': place.longitude
		})
	return get_ok_response('get_place', content)


@csrf_exempt
def set_user_places(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	username = request.session['user_name']
	request_data = json.loads(request.body)
	old_name, new_name = request_data['old_name'], request_data['new_name']
	lon, lat = request_data['longitude'], request_data['latitude']
	try:
		user = User.objects.get(name=username)
	except:
		reason = 'Username not exist.'
		return get_error_response(reason)
	place = Place.objects.get(name=old_name, user=user)
	same_place = Place.objects.filter(name=new_name, user=user)
	if same_place:
		reason = 'Place name already exist.'
		return get_error_response(reason)
	place.name = new_name
	place.longitude = lon
	place.latitude = lat
	place.save()
	return get_ok_response('set_place')


@csrf_exempt
def add_user_places(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	username = request.session['user_name']
	request_data = json.loads(request.body)
	name = request_data['name']
	lon, lat = request_data['longitude'], request_data['latitude']
	if not (0 < lon < 180 and 0 < lat < 90):
		reason='Invalid longitude/latitude.'
		return get_error_response(reason)
	user = User.objects.get(name=username)
	same_place = Place.objects.filter(name=name, user=user)
	if same_place:
		reason = 'Place name already exist.'
		return get_error_response(reason)
	Place.objects.create(
		name=name,
		user=user,
		longitude=lon,
		latitude=lat,
	)
	return get_ok_response('add_place')


@csrf_exempt
def delete_user_places(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	request_data = json.loads(request.body)
	username = request.session['user_name']
	name = request_data['name']
	user = User.objects.get(name=username)
	try:
		place = Place.objects.get(name=name, user=user)
	except:
		reason='Place not exist.'
		return get_error_response(reason)
	place.delete()
	return get_ok_response('delete_place')


@csrf_exempt
def get_user_devices(request):
	if 'is_login' not in request.session:
		reason = 'Already logout.'
		return get_error_response(reason)
	username = request.session['user_name']
	place_set = Place.objects.filter(user__name=username)
	content = []
	translate = {
		'online': '在线',
		'offline': '离线',
		'malfunction': '故障',
	}
	for place in place_set:
		device_set = Device.objects.filter(location__id=place.id)
		for device in device_set:
			content.append({
				'name': device.name,
				'status': translate[device.status],
				'location': device.location.name,
			})
	return get_ok_response('get_device', content)


@csrf_exempt
def set_user_devices(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	request_data = json.loads(request.body)
	username = request.session['user_name']
	loc_name_old, dev_name_old = request_data['loc_name_old'], request_data['dev_name_old']
	loc_name_new, dev_name_new = request_data['loc_name'], request_data['dev_name']
	translate = {
		'在线': 'online',
		'离线': 'offline',
		'故障': 'malfunction',
	}
	raw_status = request_data['status']
	# assert raw_status in translate
	if raw_status not in translate:
		reason='Invalid status.'
		return get_error_response(reason)
	status = translate[raw_status]
	user = User.objects.get(name=username)
	try:
		loc_old = Place.objects.get(name=loc_name_old, user=user)
		loc_new = Place.objects.get(name=loc_name_new, user=user)
	except:
		reason='Place not exist.'
		return get_error_response(reason)
	try:
		dev = Device.objects.get(name=dev_name_old, location=loc_old)
	except:
		reason='Device not exist.'
		return get_error_response(reason)
	dev.name = dev_name_new
	dev.location = loc_new
	dev.status = status
	dev.save()
	return get_ok_response('set_device')


@csrf_exempt
def add_user_devices(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	request_data = json.loads(request.body)
	username = request.session['user_name']
	loc_name, dev_name = request_data['loc_name'], request_data['dev_name']
	translate = {
		'在线': 'online',
		'离线': 'offline',
		'故障': 'malfunction',
	}
	raw_status = request_data['status']
	if raw_status not in translate:
		reason='Invalid status.'
		return get_error_response(reason)
	status = translate[raw_status]
	user = User.objects.get(name=username)
	loc = Place.objects.get(name=loc_name, user=user)
	same_dev = Device.objects.filter(name=dev_name, location=loc)
	if same_dev:
		reason = 'Device name already exist.'
		return get_error_response(reason)
	Device.objects.create(
		name=dev_name,
		status=status,
		location=loc,
	)
	return get_ok_response('add_device')


@csrf_exempt
def delete_user_devices(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	username = request.session['user_name']
	request_data = json.loads(request.body)
	loc_name, dev_name = request_data['loc_name'], request_data['dev_name']
	user = User.objects.get(name=username)
	try:
		loc = Place.objects.get(name=loc_name, user=user)
	except:
		reason='Place not exist.'
		return get_error_response(reason)
	try:
		dev = Device.objects.get(name=dev_name, location=loc)
	except:
		reason='Device not exist.'
		return get_error_response(reason)
	dev.delete()
	return get_ok_response('delete_device')


@csrf_exempt
def add_user_order(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	username = request.session['user_name']
	request_data = json.loads(request.body)
	
	translate = {
		'物理损坏': 'physical damage',
		'无法启动': 'unable to start',
		'无法进出': 'unable to enter in/out',
		'其他原因': 'other',
	}
	if request_data['order_type'] not in translate:
		reason='Invalid order type.'
		return get_error_response(reason)
	order_type, description = translate[request_data['order_type']], request_data['description']
	device_id = request_data['id']
	user = User.objects.get(name=username)
	try:
		device = Device.objects.get(pk=device_id)
	except:
		reason='Invalid device ID.'
		return get_error_response(reason)
	Order.objects.create(
		consumer=user,
		device=device,
		order_type=order_type,
		description=description,
	)
	return get_ok_response('add_order')


@csrf_exempt
def get_user_orders(request):
	if 'is_login' not in request.session:
		reason = 'Already logout.'
		return get_error_response(reason)
	username = request.session['user_name']
	place_set = Place.objects.filter(user__name=username)
	content = []
	translate = {
		'physical damage': '物理损坏',
		'unable to start': '无法启动',
		'unable to enter in/out': '无法进出',
		'other': '其他原因',
	}
	for place in place_set:
		device_set = Device.objects.filter(location__id=place.id)
		for device in device_set:
			order_set = Order.objects.filter(device__id=device.id)
			for order in order_set:
				content.append({
					'device': device.name,
					'description': order.description,
					'type': translate[order.order_type],
				})
	return get_ok_response('get_order', content)


@csrf_exempt
def get_user_asset(request):
	if 'is_login' not in request.session:
		reason = 'Already logout.'
		return get_error_response(reason)
	username = request.session['user_name']
	user = User.objects.get(name=username)
	content = [{'asset': user.asset}]
	return get_ok_response('get_asset', content)


@csrf_exempt
def set_user_asset(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	username = request.session['user_name']
	request_data = json.loads(request.body)
	new_asset = request_data['asset']
	user = User.objects.get(name=username)
	user.asset = new_asset
	user.save()
	return get_ok_response('set_asset')


@csrf_exempt
def get_user_deal(request):
	if 'is_login' not in request.session:
		reason = 'Already logout.'
		return get_error_response(reason)
	username = request.session['user_name']
	user = User.objects.get(name=username)
	deal_set = Deal.objects.filter(consumer=user)
	content = []
	for deal in deal_set:
		content.append({
			'location': deal.location.name,
			'device': deal.device.name,
			'device_id': deal.device.id,
			'start_time': deal.start_time,
			'end_time': deal.end_time,
		})
	return get_ok_response('get_deal', content)


@csrf_exempt
def add_user_deal(request):
	reason = check_cookie_post(request)
	if reason != 'ok':
		return get_error_response(reason)
	username = request.session['user_name']
	request_data = json.loads(request.body)
	start_time, end_time = request_data['start_time'], request_data['end_time']
	device_id = request_data['id']
	user = User.objects.get(name=username)
	try:
		device = Device.objects.get(pk=device_id)
	except:
		reason='Invalid device ID.'
		return get_error_response(reason)
	place = device.location
	Deal.objects.create(
		consumer=user,
		device=device,
		location=place,
		start_time=start_time,
		end_time=end_time
	)
	return get_ok_response('add_deal')


@csrf_exempt
def get_user_profile(request):
	if 'is_login' not in request.session:
		reason = 'Already logout.'
		return get_error_response(reason)
	username = request.session['user_name']
	user = User.objects.get(name=username)
	content = [{
		'name': username,
		'email': user.email,
		'created_time': int(user.created_time.timestamp() * 1000),
		'asset': user.asset,
		'auth': user.auth,
	}]
	return get_ok_response('get_user_profile', content)


def send_register_email(email, username, confirm_code):
	subject = f'Registration Confirm: {username}'
	text_content = 'This is a registration confirmation.'
	url_part='localhost:8000' if sys.argv[1]=='test' else sys.argv[2]
	url = f'http://{url_part}/users/confirm/?code={confirm_code}'
	html_content = f'<p>Click <a href="{url}" target="blank">this</a> to accomplish the confirmation.</p>'
	message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
	message.attach_alternative(html_content, 'text/html')
	message.send()


def send_reset_email(email, username, new_psw):
	subject = f'Reset Password: {username}'
	text_content = f'This includes a reset password for user {username}'
	html_content = f'''<p>This includes a reset password for user {username}.</p>
    <p>Your temporary password is {new_psw}. Please change it after login.'''
	message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
	message.attach_alternative(html_content, 'text/html')
	message.send()


def inject_places_wrapper(request):
	inject_places()
	return get_ok_response('inject_places')


def inject_places():
	with open('./scripts/places.json', 'r', encoding='utf-8') as fp:
		places_str = fp.read()
	places = json.loads(places_str)['places']
	for place in places:
		user = User.objects.get(name=place['user'])
		Place.objects.get_or_create(
			name=place['name'],
			user=user,
			latitude=place['lat'],
			longitude=place['lon']
		)


def inject_devices_wrapper(request):
	inject_devices()
	return get_ok_response('inject_devices')


def inject_devices():
	with open('./scripts/devices.json', 'r', encoding='utf-8') as fp:
		devices_str = fp.read()
	devices = json.loads(devices_str)['devices']
	place_list = list(Place.objects.all())
	for device in devices:
		name, status = device['name'], device['status']
		place = choice(place_list)
		Device.objects.get_or_create(
			name=name,
			status=status,
			location=place,
		)


def inject_orders_wrapper(request):
	inject_orders()
	return get_ok_response('inject_orders')


def inject_orders():
	with open('./scripts/orders.json', 'r', encoding='utf-8')as fp:
		orders_str = fp.read()
	orders = json.loads(orders_str)['orders']
	for order in orders:
		consumer, device_name = order['consumer'], order['device']
		order_type, description = order['type'], order['description']
		user = User.objects.get(name=consumer)
		device = Device.objects.get(name=device_name)
		Order.objects.get_or_create(
			consumer=user,
			device=device,
			order_type=order_type,
			description=description,
		)
