from django.db import models


class User(models.Model):
	name = models.CharField(max_length=128, unique=True, verbose_name='User name')
	psw = models.CharField(max_length=256, verbose_name='password')
	email = models.EmailField(unique=True)
	created_time = models.DateTimeField(auto_now_add=True)
	has_confirmed = models.BooleanField(default=False)
	asset = models.IntegerField(default=60, verbose_name='account asset')
	auth = models.CharField(max_length=64, default='consumer', verbose_name='authority')
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['-created_time']
		verbose_name = 'User'
		verbose_name_plural = 'Users'


class Place(models.Model):
	name = models.CharField(max_length=64, verbose_name='place name')
	user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
	latitude = models.FloatField()
	longitude = models.FloatField()
	created_time = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']
		verbose_name = 'Place'
		verbose_name_plural = 'Places'


class Device(models.Model):
	name = models.CharField(max_length=64, unique=True, verbose_name='device name')
	status = models.CharField(max_length=32, default='offline', verbose_name='device status')
	location = models.ForeignKey(Place, on_delete=models.CASCADE)
	created_time = models.DateTimeField(auto_now_add=True)
	changed_time = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['location']
		verbose_name = 'Device'
		verbose_name_plural = 'Devices'


class Deal(models.Model):
	consumer = models.ForeignKey(User, on_delete=models.CASCADE)
	device = models.ForeignKey(Device, on_delete=models.CASCADE)
	location = models.ForeignKey(Place, on_delete=models.CASCADE)
	start_time = models.BigIntegerField(verbose_name='start time')
	end_time = models.BigIntegerField(verbose_name='end time')
	
	def __str__(self):
		return '-'.join([self.consumer.name, self.location.name, self.device.name])


class Order(models.Model):
	consumer = models.ForeignKey(User, on_delete=models.CASCADE)
	device = models.ForeignKey(Device, on_delete=models.CASCADE)
	order_type = models.CharField(max_length=64, default='other', verbose_name='order type')
	description = models.CharField(max_length=4096)
	created_time = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.device.__str__() + '-' + self.consumer.__str__()
	
	class Meta:
		verbose_name = 'Order'
		verbose_name_plural = 'Orders'


class ConfirmString(models.Model):
	code = models.CharField(max_length=256, verbose_name='confirm code')
	user = models.OneToOneField('User', on_delete=models.CASCADE)
	created_time = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.user.name + ': ' + self.code
	
	class Meta:
		ordering = ['-created_time']
		verbose_name = 'Confirm Code'
		verbose_name_plural = 'Confirm Codes'
