#!/usr/bin/env python

import socket, select, copy, struct

# Maximum TTL before we abort
MaxHops = 30
# How many seconds before we abort a certain TTL step
Timeout = 5
# If debug is enabled we print every step as received
Debug = False

"""
Traceroute implementation based on: 
 https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your
However, unlike that example I implement the black magic used in BSD
to solve the multiple copies of traceroute problem.
You can read what I mean in the FreeBSD source code:
    /usr/src/contrib/traceroute/traceroute.c

I use random numbers instead of PIDs, but it's the same principle.
I also used example code to parse the ICMP header myself:
    https://gist.github.com/pklaus/856268
"""
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
			#send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
			# Luke, you switched off your targeting computer! What's wrong?
			# Nothing. I'm alright. Just writing all my packets by hand.
			send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
		except socket.error:
			print "Unable to create raw socket. Try running as root?"
			return

		# Set up our sockets and send a UDP probe to our next hop
		try:
			send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
			recv_socket.bind(("", port + ttl))
			send_socket.bind(("", port + ttl)) # THIS IS ESSENTIAL FOR BLACK MAGIC
			probe = makeProbe(port + ttl, ttl, dest, port + ttl, port + ttl)
			send_socket.sendto(probe, (dest, port + ttl))
		except socket.error:
			print "Unable to bind to port %d, perhaps it's already in use?" % (port)
			return

		# Okay, now let's try to receive an ICMP echo response for that UDP probe
		# This may or may not succeed, depending on the host we sent to
		addr = None
		try:
			# We use select to enforce a timeout. We also need to ignore packets
			# destined for other traceroute instances.
			while( True ):
				ready = select.select([recv_socket], [], [], Timeout)
				if( ready[0] ):
					# Blocksize doesn't matter much, we use 512
					data, src = recv_socket.recvfrom(512)
					n = len(data)
					sig = getICMPid(data)
					src = src[0] # Extract just IP, not port
					if( Debug ):
						print "Read %d bytes from %s with signature: %s" % (n, src, sig)
					if( sig >= port and sig <= port + MaxHops ):
						addr = src
						break
				else:
					break
		except socket.error:
			pass
		finally:
			send_socket.close()
			recv_socket.close()

		# Okay, at this point we're done trying to receive a packet.
		# We either got an appropriate one from 'addr', or we hit
		# our timeout and 'addr' is set to None.

		if( addr is None ):
			addr = "*"

		if( Debug ):
			print "%d\t%s" % (ttl, addr)
	
		# Record the newly found hop in the route.	
		route += [copy.deepcopy(addr)]
		ttl += 1

		# If we're done then record our route in the global routing list
		if( addr == dest or ttl > MaxHops ):
			with lock:
				routes += [route]
				print "Host '%s' reached. Hops: %d" % (host, ttl)
			break

"""
 I read how to make a raw IP header from:
	https://stackoverflow.com/questions/24520799
"""
def makeProbe(_id, ttl, dest, srcPrt, dstPrt):
	version = 4 # IPv4
	ihl = 5     # Header length in 32-bit words (5 words == 20 bytes)
	DF = 0      # Optional fields, leaving them blank
	# Length will be filled in by kernel
	Tlen = 0   # Length of data (0) + 20 bytes for ipv4 header + 8 byte udp
	ID = _id    # ID of packet
	Flag = 0    # Flags and fragment offset
	TTL = ttl   # Time to live
	Proto = socket.IPPROTO_UDP # Protocol 17, UDP
	ip_checksum = 0 # Checksum will be automatically filled in
	SIP = socket.inet_aton("0.0.0.0")
	DIP = socket.inet_aton(dest)
	ver_ihl = ver_ihl = (version << 4) + ihl
	#f_f = (Flag << 13) + Fragment
	#ip_hdr =  struct.pack("!BBHHHBBH4s4s", ver_ihl,DF,Tlen,ID,f_f,TTL,Proto,ip_checksum,SIP,DIP)
	#return ip_hdr
	IP_HEADER = struct.pack(
		"!"        # Network (Big endian)
		"2B"       # Version and IHL, DSCP, and ECN
		"3H"       # Total length, ID, Flags and fragment offset
		"2B"       # TTL, protocol
		"H"        # Checksum
		"4s"       # Source IP
		"4s"       # Dest IP
		, ver_ihl, DF, Tlen, ID, Flag, TTL, Proto, ip_checksum, SIP, DIP)

	# UDP uses "source port, dest port, length, checksum
	UDP_HEADER = struct.pack("!4H", srcPrt, dstPrt, 8, 0)
	return IP_HEADER + UDP_HEADER


"""
 This parses the header of an ICMP packet and returns the ID
 Heavily draws from https://gist.github.com/pklaus/856268
"""
def getICMPid(packet):
	icmp_header = packet[20:]
	_type, code = struct.unpack('bb', icmp_header[:2])
	#_type, code, checksum, unused = struct.unpack('bbHL', icmp_header[:8])
	
	# We only care about responses to traceroute (type 11 code 0)
	if( _type != 11 ):
		return -1

	# ICMP header for type 11 will be:
	# Type / code (2 bytes)
	# Checksum (2 bytes)
	# Unused (4 bytes)
	#
	# That's a total of 8 bytes used. After that we have:
	# IP header (20 bytes?)
	# 8 Bytes of UDP header data
	# So if we just care about the UDP part we should skip 48 bytes in, for:
	# Original IP header (20) + ICMP header (8) + 2nd IP header (20)
	
	# The above math is a little off. By manual examination of the packets
	# in wireshark we know we need to scroll in 52, not 48. Why? Magic.

	return struct.unpack_from('!H', packet, 52)[0]

	#header = packet[28:56]
	#ip_header = header[:20]
	#udp_data = header[20:]
	#udp_src_port = struct.unpack('H', udp_data[:2])
	#return udp_src_port

	"""
	print "Type: %s" % (str(_type))
	print "Code: %s" % (str(code))
	print "Checksum: %s" % (str(checksum))
	print "ID: %s" % (str(_id))
	print "Sequence: %s" % (str(sequence))
	return _id
	"""
