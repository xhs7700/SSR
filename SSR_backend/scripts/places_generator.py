import json
from random import uniform

if __name__ == '__main__':
	places = {'places': []}
	n = 20
	for i in range(n):
		name = f'地点 {i + 1}'
		user = 'xhs'
		lat = uniform(25, 40)
		lon = uniform(100, 117)
		places['places'].append({
			'name': name,
			'user': user,
			'lat': lat,
			'lon': lon,
		})
	with open('./places.json', 'w', encoding='utf-8') as fp:
		places_str = json.dumps(places, ensure_ascii=False, indent=2)
		fp.write(places_str)
