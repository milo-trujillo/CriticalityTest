#!/usr/bin/env python

import socket, select, copy

# Maximum TTL before we abort
MaxHops = 30
# How many seconds before we abort a certain TTL step
Timeout = 5
# If debug is enabled we print every step as received
Debug = False

# Traceroute implementation based on: 
# https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your
def traceroute(host, port, routes, lock):
	dest = socket.gethostbyname(host)
	icmp = socket.getprotobyname('icmp')
	udp = socket.getprotobyname('udp')
	ttl = 1
	route = []

	with lock:
		print "Attempting to reach %s at %s using port %d" % (host, dest, port)
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
			# Use select to enforce a timeout
			ready = select.select([recv_socket], [], [], Timeout)
			if( ready[0] ):
				_, addr = recv_socket.recvfrom(512) # Blocksize doesn't matter a ton
				addr = addr[0] # We just want IP, not port number
		except socket.error:
			pass
		finally:
			send_socket.close()
			recv_socket.close()

		if( addr is None ):
			addr = "*"

		if( Debug ):
			print "%d\t%s" % (ttl, addr)
		
		route += [copy.deepcopy(addr)]
		ttl += 1

		if( addr == dest or ttl > MaxHops ):
			with lock:
				routes += [route]
				print "Host '%s' reached. Hops %d." % (host, ttl)
			break
