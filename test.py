#!/usr/bin/env python

import socket, threading, random, numpy
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

# This finds the common hosts at the start of every route
def findCommonHops(routes):
	if( len(routes) == 0 ):
		return []

	# Find the shortest route - we can't have any critical hops past that length
	minLen = len(routes[0])
	for r in routes:
		if( len(r) < minLen ):
			minLen = len(r)

	data = numpy.array(routes)
	commonHops = []
	for i in range(0, minLen):
		col = data[:,i] # Extract ith column
		match = all(x == col[0] for x in col)
		if( match ):
			commonHops += [col[0]]
		else:
			return commonHops
	return commonHops 

# Reverse lookup, get a domain name for an IP address if possible
def getHostname(IP):
	try:
		name, alias, addresslist = socket.gethostbyaddr(host)
		return name
	except socket.herror:
		return "Unknown Host"

if __name__ == "__main__":
	routes = []
	routeLock = threading.RLock()
	threads = []

	random.seed()

	print "Initating test. Spinning up traceroutes to %d destinations." % (len(Hosts))
	#for i in range(0, 1):
	for i in range(0, len(Hosts)):
		host = Hosts[i]
		# Choose a random high port that's unlikely to be listened to
		port = random.randint(33434, 65500)
		worker = threading.Thread(
			target=traceroute, 
			args=(host, port, routes, routeLock))
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

	common = findCommonHops(routes)

	print "Leading common hosts in all routes: %d" % (len(common))
	for host in common:
		name = getHostname(host)
		print "%s\t(%s)" % (host, name)
