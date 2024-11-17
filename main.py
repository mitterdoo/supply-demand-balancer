from balance import System

if __name__ == '__main__':
	system = System()
	
	system.create_producer('Copper plate', 14400)
	system.create_producer('LDS', 1800)
	system.create_producer('Copper cable', 64800)

	system.create_producer('Iron plate', 14400)
	system.create_producer('Iron stick', 3600)
	system.create_producer('Iron gear wheel', 14400)
	system.create_producer('Steel', 7200)

	system.create_producer('Tungsten plate', 1800)

	system.create_producer('Concrete', 3600)

	system.create_producer('Plastic', 400)

	#######################

	# system.create_producer('Sulfuric acid', 7164.9 * 2.30)
	system.create_producer('Sulfuric acid', 1200 * 3 * 3)

	system.create_producer('Coal', 5.75 * 48)


	system.create_service('Electronic circuit', [
		system.create_consumer('Iron plate', 15210),
		system.create_consumer('Copper cable', 45630),
		system.create_producer('Electronic circuit', 18860.4)
	])

	system.create_service('Advanced circuit', [
		system.create_consumer('Electronic circuit', 4725),
		system.create_consumer('Copper cable', 9450),
		system.create_consumer('Plastic', 4725),
		system.create_producer('Advanced circuit', 2929.5)
	])

	system.create_service('Processing unit', [
		system.create_consumer('Electronic circuit', 4320),
		system.create_consumer('Advanced circuit', 432),
		system.create_consumer('Sulfuric acid', 1080),
		system.create_producer('Processing unit', 267.84)
	])

	system.balance()

	for resource in system.resources.values():
		resource.print()
		print('')
	
	print('=========================')

	for service in system.services:
		service.print()
		print('')
