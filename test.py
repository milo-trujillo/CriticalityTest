#!/usr/bin/env python

import socket

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
MaxHops = 30

# Traceroute implementation based on: 
# https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your
def traceroute(host, port):
	dest = socket.gethostbyname(host)
	icmp = socket.getprotobyname('icmp')
	udp = socket.getprotobyname('udp')
	ttl = 1
	while True:
		recv_socket = None
		send_socket = None
		
		try:
			recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
			send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
		except socket.error:
			print "Unable to create raw socket. Try running as root?"
			return

		try:
			send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
			recv_socket.bind(("", port))
			send_socket.sendto("", (dest, port))
		except socket.error:
			print "Unable to bind to port %d, perhaps it's already in use?" % (port)
			return

		addr = None
		try:
			_, addr = recv_socket.recvfrom(512) # Blocksize doesn't matter a ton
			addr = addr[0] # We just want IP, not port number
		except socket.error:
			pass
		finally:
			send_socket.close()
			recv_socket.close()

		if addr is not None:
			print "%d\t%s" % (ttl, addr)
		else:
			print "%d\t*" % (ttl, addr)
		ttl += 1

		if( addr == dest or ttl > MaxHops ):
			print "Host '%s' reached." % (host)
			break


print "Initating test. Spinning up traceroutes to " + str(len(Hosts)) + " destinations."
traceroute("google.com", BasePort)
