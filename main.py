'''
MIT License

Copyright (c) 2024 Connor Ashcroft

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

'''
If True, the solver will assume a resource with no consumers is being fully consumed.
'''
IGNORE_SURPLUS = True

class Machine:
	def __init__(self, resource_name: str, target_throughput, service=None):
		self.target_throughput = target_throughput
		self.effective_throughput = target_throughput
		self.efficiency = 1
		self.resource = resource_name
		self.service = service

	def set_effective_throughput(self, throughput):
		self.effective_throughput = throughput
		self.efficiency = throughput / self.target_throughput

	def set_efficiency(self, efficiency) -> bool:
		'''
		Returns whether the efficiency was changed from its previous value
		'''
		changed = efficiency != self.efficiency

		self.efficiency = efficiency
		self.effective_throughput = self.target_throughput * efficiency
		return changed

	def __str__(self):
		return f'{self.resource} Machine: {self.effective_throughput}/{self.target_throughput} ({self.efficiency})'

class Producer(Machine):
	producer = True
	consumer = False
	def __repr__(self):
		return f'Producer(\'{self.resource}\', {self.target_throughput:.2f}) <{self.effective_throughput:.2f} at {self.efficiency:.1%}>'

class Consumer(Machine):
	producer = False
	consumer = True
	def __repr__(self):
		return f'Consumer(\'{self.resource}\', {self.target_throughput:.2f}) <{self.effective_throughput:.2f} at {self.efficiency:.1%}>'

class Service:
	def __init__(self, service_name: str):
		self.producers = []
		self.consumers = []
		self.machines = []
		self.efficiency = 1
		self.name = service_name

	def add_machine( self, machine: Machine):
		self.machines.append(machine)

		if machine.service != None:
			machine.service.remove_machine(machine)

		machine.service = self
		if machine.producer:
			self.producers.append(machine)
		else:
			self.consumers.append(machine)

	def remove_machine(self, machine: Machine):
		try:
			self.machines.remove(machine)
			if machine.producer:
				self.producers.remove(machine)
			else:
				self.consumers.remove(machine)
		except ValueError:
			pass
		machine.service = None

	def balance(self):
		
		efficiency = 1
		for machine in self.machines:
			if machine.efficiency < efficiency:
				efficiency = machine.efficiency

		for machine in self.machines:
			machine.set_efficiency(efficiency)

	def __repr__(self):
		return f'Service(\'{self.name}\')'
	
	def print(self):
		print(f'[[ SERVICE: "{self.name}" ]]')

		efficiency = 1
		for machine in self.machines:
			if machine.efficiency < efficiency:
				efficiency = machine.efficiency
		
		print(f'\tEfficiency: {efficiency:.1%}')

		print('\tConsumes:')
		for consumer in self.consumers:
			name = consumer.resource
			effective = consumer.effective_throughput
			target = consumer.target_throughput
			if target == 0:
				machine_efficiency = 0
			else:
				machine_efficiency = effective/target
			print(f'\t\t"{name}": {effective:,.2f} / {target:,.2f} ({machine_efficiency:.1%})')

		print('\tProduces:')
		for producer in self.producers:
			name = producer.resource
			effective = producer.effective_throughput
			target = producer.target_throughput
			if target == 0:
				machine_efficiency = 0
			else:
				machine_efficiency = effective/target
			print(f'\t\t"{name}": {effective:,.2f} / {target:,.2f} ({machine_efficiency:.1%})')

class Resource:
	def __init__(self, name: str):
		self.name = name
		self.producers = []
		self.consumers = []

	def print(self):
		print(f'[[ RESOURCE: "{self.name}" ]]')
		target_production = sum([machine.target_throughput for machine in self.producers])
		target_consumption = sum([machine.target_throughput for machine in self.consumers])
		effective_production = sum([machine.effective_throughput for machine in self.producers])
		effective_consumption = sum([machine.effective_throughput for machine in self.consumers])


		if target_production < target_consumption:
			target_state = f'shortage of {target_consumption - target_production:,.2f}'
		elif target_production > target_consumption:
			target_state = f'surplus of {target_production - target_consumption:,.2f}'
		else:
			target_state = f'equal'

		if effective_production < effective_consumption:
			effective_state = f'shortage of {effective_consumption - effective_production:,.2f}'
		elif effective_production > effective_consumption:
			effective_state = f'surplus of {effective_production - effective_consumption:,.2f}'
		else:
			effective_state = f'equal'
			# wouldn't this theoretically always be equal when the system gets balanced?
		
		print(f'\tTarget: {target_production:,.2f} / {target_consumption:,.2f} ({target_state})')
		print(f'\tEffective: {effective_production:,.2f} / {effective_consumption:,.2f} ({effective_state})')


	def balance(self) -> bool:
		'''
		Return `True` if any machine was affected by the balancing
		If all resources return False, the System is perfectly balanced (as all things should be)
		'''

		production = 0
		consumption = 0
		
		consumers = 0

		machines = self.producers + self.consumers
		for machine in machines:
			efficiency = 1
			service = machine.service

			for neighbor in service.machines:
				if neighbor == machine: continue
				if neighbor.efficiency < efficiency:
					efficiency = neighbor.efficiency
				
			# do not assign this efficiency, just use it as a temporary scalar

			scaled_throughput = machine.target_throughput * efficiency

			if machine.producer:
				production += scaled_throughput
			else:
				consumers += 1
				consumption += scaled_throughput

		if IGNORE_SURPLUS and consumers == 0:
			consumption = production

		# calculate surplus/equilibrium/shortage

		changed = False

		if production > consumption:
			# surplus
			if production == 0:
				producer_efficiency = 0
			else:
				producer_efficiency = consumption / production

			for machine in machines:
				if machine.producer:
					changed = True if machine.set_efficiency(producer_efficiency) else changed
				else:
					changed = True if machine.set_efficiency(1) else changed
			
		else:
			# equal or shortage
			if consumption == 0:
				consumer_efficiency = 0
			else:
				consumer_efficiency = production / consumption
			
			for machine in machines:
				if machine.producer:
					changed = True if machine.set_efficiency(1) else changed
				else:
					changed = True if machine.set_efficiency(consumer_efficiency) else changed
		
		return changed


class System:
	'''
	Contains a collection of Producers, Consumers, and Services
	'''
	def __init__(self):
		self.producers = []
		self.consumers = []
		self.services = []
		self.resources = {}
	
	def get_resource(self, name: str):
		if name not in self.resources:
			self.resources[name] = Resource(name)
		return self.resources[name]

	def create_producer(self, resource_name: str, target_throughput) -> Producer:
		resource = self.get_resource(resource_name)
		producer = Producer(resource_name, target_throughput)
		resource.producers.append(producer)
		self.producers.append(producer)

		self.create_service(f'AUTO: {resource_name} Producer', [producer])

		return producer

	def create_consumer(self, resource_name: str, target_throughput) -> Consumer:
		resource = self.get_resource(resource_name)
		consumer = Consumer(resource_name, target_throughput)
		resource.consumers.append(consumer)
		self.consumers.append(consumer)

		self.create_service(f'AUTO: {resource_name} Consumer', [consumer])
		return consumer
	
	def create_service(self, service_name: str, machines) -> Service:
		service = Service(service_name)
		for machine in machines:
			service.add_machine(machine)

		self.services.append(service)
		return service
	
	def cleanup_empty_services(self):
		to_remove = []
		for service in self.services:
			if len(service.machines) == 0:
				to_remove.append(service)
		
		[self.services.remove(service) for service in to_remove]

	def balance(self):
		self.cleanup_empty_services()
		count = 0
		for i in range(1000):
			if i == 999:
				raise OverflowError('Could not solve the System. Make sure there are no feedback loops present.')
			changed = False
			for resource in self.resources.values():
				changed = True if resource.balance() else changed
			
			if not changed:
				break
			count += 1
		
		for service in self.services:
			service.balance()

		print(f'balanced in {count} iteration(s)')
	

if __name__ == '__main__':
	system = System()
	
	MINING_PRODUCTIVITY = 0.9

	drills = {
		'Iron ore': [
			116,
			78,
			12,
			49
		],
		'Copper ore': [
			112,
			53,
			69,
			76
		],
		'Stone': [
			89,
			20,
			25
		],
		'Coal': [
			84
		]
	}

	# Ore drills
	for name in drills:
		drill_list = drills[name]
		total = 0
		for drill_count in drill_list:
			total += drill_count * (1 + MINING_PRODUCTIVITY) * 30
		system.create_producer(name, total)

	# Smelting array
	system.create_service('Iron smelting',[
		system.create_consumer('Iron ore', 1800 * 14),
		system.create_producer('Iron', 1800 * 14)
	])

	system.create_service('Copper smelting', [
		system.create_consumer('Copper ore', 1800 * 4),
		system.create_producer('Copper', 1800 * 4)
	])

	system.create_service('Stone smelting', [
		system.create_consumer('Stone', 1800 * 1),
		system.create_producer('Stone brick', 1800 * 1)
	])

	system.create_service('Steel smelting', [
		system.create_consumer('Iron', 1800*10),
		system.create_producer('Steel', 1800 * 2)
	])

	system.balance()

	for resource in system.resources.values():
		resource.print()
		print('')
	
	print('=========================')

	for service in system.services:
		service.print()
		print('')

