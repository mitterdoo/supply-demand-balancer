

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

	'''
	def scale_supply_demand(self):
		smallest_efficiency = 1

		for machine in self.machines:
			if machine.efficiency < smallest_efficiency:
				smallest_efficiency = machine.efficiency
		
		for machine in self.machines:
			machine.set_efficiency(smallest_efficiency)
		
		self.efficiency = smallest_efficiency
		'''
	

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

	'''
	def scale_supply_demand(self):
		total_supply = sum([producer.effective_throughput for producer in self.producers])
		total_demand = sum([consumer.effective_throughput for consumer in self.consumers])

		if total_supply > total_demand:
			# Scale down producers
			for producer in self.producers:
				if total_supply == 0:
					producer.set_effective_throughput(0)
				else:
					producer.set_effective_throughput(producer.effective_throughput * (total_demand / total_supply))
		else:
			# Scale down consumers
			for consumer in self.consumers:
				if total_demand == 0:
					consumer.set_effective_throughput(0)
				else:
					consumer.set_effective_throughput(consumer.effective_throughput * (total_supply / total_demand))
	'''
	def print(self):
		print(f'[[ RESOURCE: "{self.name}" ]]')
		effective_production = sum([machine.effective_throughput for machine in self.producers])
		effective_consumption = sum([machine.effective_throughput for machine in self.consumers])

		if effective_production < effective_consumption:
			state = 'shortage'
		elif effective_production > effective_consumption:
			state = 'surplus'
		else:
			state = 'equal'
			# wouldn't this theoretically always be equal when the system gets balanced?
		
		print(f'\t{effective_production:,.2f} / {effective_consumption:,.2f} ({state})')


	def balance(self) -> bool:
		'''

		Return `True` if any machine was affected by the balancing
		If all resources return False, the System is perfectly balanced (as all things should be)

		1. Iterate through producers and add their calculated effective throughputs
			a. Calculate effective throughput of a producer by scaling down its target throughput by its least efficient neighbor's percentage.
				Do not write value to machine.
		2. Iterate through consumers using the same method as above
		3. If surplus:
			a. Scale down each consumer's effective throughput 
		'''

		production = 0
		consumption = 0
		
		machines = self.producers + self.consumers
		for machine in machines:
			efficiency = 1
			service = machine.service

			for neighbor in service.machines:
				if neighbor == machine: continue
				if neighbor.efficiency < efficiency:
					efficiency = neighbor.efficiency
				
			# do not assign this efficiency, just use it as a temporary scalar unless told to write

			scaled_throughput = machine.target_throughput * efficiency

			if machine.producer:
				production += scaled_throughput
			else:
				consumption += scaled_throughput

			
			
		
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
			count += 1
			if i == 999:
				raise OverflowError('Could not solve the System. Make sure there are no feedback loops present.')
			changed = False
			for resource in self.resources.values():
				changed = True if resource.balance() else changed
			
			if not changed:
				break
		
		for service in self.services:
			service.balance()

		print(f'balanced in {count} iteration(s)')
	
	'''
	def scale_supply_demand(self):
		for _ in range(10):
			for resource in self.resources.values():
				resource.scale_supply_demand()
			for service in self.services:
				service.scale_supply_demand()
	'''
	

if __name__ == '__main__':
	system = System()
	
	iron_ore_producer = system.create_producer('Green', 0)

	a = system.create_service('A',[
		system.create_consumer('Green', 2),
		system.create_producer('Blue', 4)
	])

	b = system.create_service('B',[
		system.create_consumer('Blue', 5),
		system.create_producer('Red', 5)
	])

	c = system.create_service('C', [
		system.create_consumer('Blue', 3),
		system.create_consumer('Green', 2)
	])

	system.balance()

	for resource in system.resources.values():
		resource.print()
		print('')
	
	print('=========================')

	for service in system.services:
		service.print()
		print('')

	hello = 2

