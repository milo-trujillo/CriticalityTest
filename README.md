# Criticality Test

*Milo Trujillo*

The Internet is a hybrid system - at a high level it is widely decentralized and redundant, but at local levels the network topology is often very rigidly structured. But how centralized *is* our network connection? How many ‘hops’ out to the Internet are critical hubs, any one of which failing would cut us off from the wider world?

This is a tool for auto-detecting the degree of local network centralization. This tool will explore routing information to reach a number of geographically diverse servers (three across the United States, more in Japan, India, Australia, and England). In a decentralized network the routes to reach each of these systems would be completely different. However, by identifying the overlaps between these routes we can determine how many systems are “critical hubs” all of our traffic must flow through before reaching the larger web.

**NOTE**

At present this tool is only known to work on OSX. It will probably run correctly on any BSD system. However, it does *not* work on Linux systems. I think the Linux kernel steps on one of the IP or UDP headers I create and overrides information I was using for tracking responses.
