#!/usr/bin/env python

import socket, threading, random
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

random.seed()

print "Initating test. Spinning up traceroutes to " + str(len(Hosts)) + " destinations."
#for i in range(0, 1):
for i in range(0, len(Hosts)):
	host = Hosts[i]
	port = random.randint(33434, 65500) # Max is a little less than u_short max
	worker = threading.Thread(target=traceroute, args=(host, port, routes, routeLock))
	threads += [worker]
	worker.start()

print "Please be patient, it can take a few minutes to collect our data..."

for i in range(0, len(threads)):
	threads[i].join()

print ""
print "================================================"
print "All traceroutes complete. Summary is as follows."
print "================================================"
print ""

commonHosts = []
tmp = None
for i in range(0, 200):
	for j in range(0, len(routes)):
		route = routes[j]
		if( i < len(route) ):
			if( j == 0 ):
				tmp = route[i]
			if( tmp != route[i] ):
				break
			if( j == len(routes) - 1 ):
				commonHosts += [tmp]

print "Common hosts in all routes: %d" % (len(commonHosts))
for host in commonHosts:
	print host
