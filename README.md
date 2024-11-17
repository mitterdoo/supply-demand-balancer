# supply-demand-balancer
A Python proof of concept for a generic balancer/solver for any arbitrary supply/demand system of services

This was made for use in the video game Factorio, which deals with the concept of supply and demand in many different ways.

## Overview
The idea behind this tool is to create a small Python script outlining a system of producers and consumers of arbitrary resources. Once those are plugged in, the entire system can balance the supply and demand of resources to work at its maximum possible efficiency.

The end result will highlight bottlenecked machines to aid in troubleshooting and refactoring the system for improvements.

Everything within a System assumes there is no throughput limit between machines. If one were to use this for Factorio, this does not factor in belt speeds.

## Synopsis

Include the `balance` Python module in your script.

Also refer to `main.py` for another example use case (I was using it for my Vulcanus base in Factorio).

```python
from balance import System

if __name__ == '__main__':
	s = System()

	s.create_producer('Green', 4)

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
```
Running the code above yields the below result:
```
balanced in 3 iteration(s)
[[ RESOURCE: "Green" ]]
        Target: 4.00 / 4.00 (equal)
        Effective: 3.50 / 3.50 (equal)
[[ RESOURCE: "Blue" ]]
        Target: 4.00 / 8.00 (shortage of 4.00)
        Effective: 3.00 / 3.00 (equal)
[[ RESOURCE: "Red" ]]
        Target: 5.00 / 0.00 (surplus of 5.00)
        Effective: 0.00 / 0.00 (equal)

=========================
[[ SERVICE: "AUTO: Green Producer" ]]
        Efficiency: 87.5%
        Consumes:
        Produces:
!!!             "Green": 3.50 / 4.00 (87.5%)

[[ SERVICE: "Service A" ]]
        Efficiency: 75.0%
        Consumes:
                "Green": 1.50 / 2.00 (75.0%)
        Produces:
!!!             "Blue": 3.00 / 4.00 (75.0%)

[[ SERVICE: "Service B" ]]
        Efficiency: 0.0%
        Consumes:
                "Blue": 0.00 / 5.00 (0.0%)
        Produces:
!!!             "Red": 0.00 / 5.00 (0.0%)

[[ SERVICE: "Service C" ]]
        Efficiency: 100.0%
        Consumes:
                "Blue": 3.00 / 3.00 (100.0%)
                "Green": 2.00 / 2.00 (100.0%)
        Produces:
```
Here is a diagram showing the example system of machines:

![Diagram of the above example](https://i.imgur.com/kcD5IPb.png)

## Explanation

In the scenario shown above, Service B ends up being shut off because there are no consumers of the Red resource. This reduces the Blue demand, allowing the other consumer of Blue (at 3 units/m, from Service C) to get the resources it needs.

Ultimately this ends up propagating "upstream" into Service A, since it only needs to produce 3 Blue instead of 4. The Green demand is reduced as well, thus the production of Green is reduced to meet the demand.

In the output of the program, `!!!` being printed before a machine denotes that it is bottlenecking the service that it's in. In this case, the Blue producer is slowing down Service A to meet the smaller demand.

### Key terms
- **System** - a collection of Machines, the Resources they use, and any Services they belong to.
- **Resource** - an arbitrary resource (e.g. Iron plate, Copper ore, )
- **Machine** - either a producer or consumer of a Resource. Machines require a target throughput value for the solver to work. \
Note this is not necessarily an actual machine, if you're using this for Factorio.
- **Service** - a set of Machines with their throughputs *linked* together such that they will scale down in proportion.

