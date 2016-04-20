#!/usr/bin/env python

import socket
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

print "Initating test. Spinning up traceroutes to " + str(len(Hosts)) + " destinations."
for host in Hosts:
	print "Attempting to reach %s at %s" % (host, socket.gethostbyname(host))
	traceroute(host, BasePort)
