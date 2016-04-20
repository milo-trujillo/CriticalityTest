#!/usr/bin/env python

import socket, threading
from traceroute import traceroute

"""
	The following hosts were chosen because we confirmed that their webhosting
	is located at the locations their names specify. That is, we send a
	traceroute to:
		- Seattle, Washington
		- Austin, Texas
		- Portland, Maine
		- London, UK
		- Melbourne, Australia
		- Tokyo, Japan
		- Shakarpur, India
	These destinations are geographically diverse enough that the routes taken
	should significantly differ to reach at least one.
"""
Hosts = ["www.seattle.gov", "austintexas.gov", "www1.maine.gov", "cityoflondon.gov.uk", "australia.gov.au", "www.jnto.go.jp", "india.gov.in"]
Timeout = 120 # Maximum seconds to spend reaching any destination
BasePort = 33434 # Traceroute uses ports 33434 through 33534

routes = []
routeLock = threading.RLock()
threads = []

print "Initating test. Spinning up traceroutes to " + str(len(Hosts)) + " destinations."
#for i in range(0, 1):
for i in range(0, len(Hosts)):
	host = Hosts[i]
	worker = threading.Thread(target=traceroute, args=(host, BasePort + i, routes, routeLock))
	threads += [worker]
	worker.start()

for i in range(0, len(threads)):
	threads[i].join()

print "All traceroutes complete."
print "========================="

for i in range(0, len(routes)):
	print "To reach host " + str(i)
	print str(routes[i])
