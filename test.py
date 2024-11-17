from balance import System

if __name__ == '__main__':
	s = System()

	s.create_producer('Green', 2)

	s.create_service('Service A', [
		s.create_consumer('Green', 2),
		s.create_producer('Blue', 4)
	])

	s.create_service('Service B', [
		s.create_consumer('Blue', 5),
		s.create_producer('Red', 5)
	])

	s.create_service('Service C', [
		s.create_consumer('Blue', 3),
		s.create_consumer('Green', 2)
	])

	s.balance()

	s.print()
