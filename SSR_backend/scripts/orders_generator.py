import json
from random import randint, choice

if __name__ == '__main__':
	orders = {'orders': []}
	order_type_list = ['unable to start', 'physical damage', 'unable to enter in/out', 'other']
	for i in range(10):
		consumer = f'consumer {i + 1}'
		for j in range(10):
			device = f'设备 {randint(1, 100)}'
			order_type = choice(order_type_list)
			description = f'This is a work order description typed "{order_type}": Lorem ipsum dolor sit amet, ' \
			              f'consectetur adipiscing elit. Aliquam porttitor ligula massa, vitae porta lectus imperdiet ' \
			              f'nec. Quisque quis accumsan erat. Nulla ultricies ac purus at vestibulum. Nunc eu est ' \
			              f'cursus, mattis diam sit amet, egestas massa. Suspendisse vel felis vitae velit fermentum ' \
			              f'fringilla. Quisque gravida mauris erat, sed mollis augue ultrices at. Proin mattis cursus ' \
			              f'laoreet. Suspendisse pellentesque orci tristique erat molestie tempus. Pellentesque ' \
			              f'iaculis libero id risus tincidunt, sit amet viverra leo dapibus. Curabitur id nulla lacus. ' \
			              f'Nunc at mauris sed metus tempus lacinia. Duis in lacus id ex molestie lacinia nec quis ' \
			              f'odio. Praesent varius nulla sed ipsum ullamcorper eleifend. Nulla maximus lorem quis leo ' \
			              f'euismod, nec blandit lectus auctor. Quisque gravida velit eget neque semper vehicula. ' \
			              f'Donec fringilla molestie luctus. '
			orders['orders'].append({
				'consumer': consumer,
				'device': device,
				'type': order_type,
				'description': description,
			})
	with open('./orders.json', 'w', encoding='utf-8') as fp:
		orders_str = json.dumps(orders, ensure_ascii=False, indent=2)
		fp.write(orders_str)
