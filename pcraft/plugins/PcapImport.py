from IPy import IP as IP_y
from scapy.all import Ether, CookedLinux, IP, TCP, UDP, rdpcap
from . import _utils as utils
import time
import pprint
import os

from pcraft.PluginsContext import PluginsContext


class PCraftPlugin(PluginsContext):
    name = "PcapImport"
    required = ["filename"]

    def help(self):
        helpstr="""
Import a PCAP in the current flow.

### Examples

#### Import a pcap 'phishing.pcap', and replace a bunch of IP addresses

```
action importphishing {
  exec PcapImport
  $filename = "phishing.pcap"
  field["ip"].replace("192.168.0.42" => "10.0.0.43",
                      "172.16.32.45" => "10.0.0.53",
                      "192.168.0.12" => "192.168.0.254")
}
```
"""
        return helpstr
        
    def __init__(self, ami, app, session, plugins_data):
        super().__init__(app, session, plugins_data)
        self.last_packet_time = 0
        self.reset_time()
        self.sleep_cursor = 0.0
        self.is_first = True

    def reset_time(self):
        self.last_packet_time = 0
        # self.sleep_cursor = 0.0
        
    def run(self, ami, action):
        self.reset_time()
        append_sleep = 0
        first_time = 0
        if self.is_first:
            first_time = action.GetSleepCursor()
            self.is_first = False
        else:
            append_sleep = action.GetSleepCursor() - first_time

        only_replace = None
        try:
            only_replace = action.Variables()["$onlyreplace"]
        except:
            pass
            
        amifile = ami.GetFilePath()
        amipath = os.path.dirname(os.path.realpath(amifile))
        pcap_in = os.path.join(amipath, action.Variables()["$filename"])
        print("Importing PCAP: %s" % pcap_in)

        to_replace = action.FieldActions()

        n_items_replaced = 0
        packets_injected = 0
        
        ip_list = None
        try:
            ip_list = to_replace["ip"]["replace"]
        except:
            pass # That means we have no definition to replace, we won't replace then

        packets = rdpcap(pcap_in)
        last_packet = None
        seq = 0
        for packet in packets:
            packet_time = int(packet.time)
            sleep_delta = 0
            
            if packet_time > self.last_packet_time:
                # print("%s > %s" % (packet_time, self.last_packet_time))
                if self.last_packet_time != 0:
                    sleep_delta = packet_time - self.last_packet_time
                self.last_packet_time = packet_time

            self.sleep_cursor += float(sleep_delta)
            # print("New sleep cursor:%f" % new_sleep_cursor)
            action.SetSleepCursor(self.sleep_cursor + append_sleep)
            
            if CookedLinux in packet:
                packet = Ether() / packet.payload
                        
            try:
                del packet[IP].chksum
                del packet[TCP].chksum
                del packet[UDP].chksum
            except IndexError:
                pass

            if ip_list:
                ip_to_replace = None
                for k, v in ip_list.items():
                    we_replaced = False
                    ip_to_replace = k
                    ip_replacement = IP_y(v)

                    if packet.haslayer(IP):
                        if packet[IP].src == ip_to_replace:
                            packet[IP].src = str(ip_replacement)
                            n_items_replaced += 1
                            we_replaced = True
                        if packet[IP].dst == ip_to_replace:
                            packet[IP].dst = str(ip_replacement)
                            n_items_replaced += 1
                            we_replaced = True

                if we_replaced and only_replace:
                    self.plugins_data.AddPacket(action, packet)
                    packets_injected += 1
                else:
                    if not only_replace:
                        self.plugins_data.AddPacket(action, packet)
                        packets_injected += 1

                    # seq += 1
                last_packet = packet
                            
            else: # if ip_list
                self.plugins_data.AddPacket(action, packet)
                packets_injected += 1
                
        print("%s replaced %d items" % ( self.name, n_items_replaced) )
        print("Imported %d packets" % (packets_injected) )
            
        return self.plugins_data
