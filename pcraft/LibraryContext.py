import random
import uuid
import hashlib
import geoip2.database
import os
import ipaddress
import string

from . import utils
from .VariablesState import VariablesState
from .VirtualPacket import *

from .confnames import *

class LibraryContext(object):
    def __init__(self, service=None):
        self.service = service
        self.built_variables = {}
        self.varstate = VariablesState()
        self.virtual_packets = []
        self.user_agents = ["Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44", "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1", "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/38.1  Mobile/15E148 Safari/605.1.15", "ELinks/0.11.7 (textmode; Darwin 20.6.0 x86_64; 143x43-2)", "Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0", "Mozilla/5.0 (X11; Linux x86_64) KIO/5.86 konqueror/21.08.2", "Wget/1.21.2", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44", "Lynx/2.9.0dev.10 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/3.7.2", "URL/Emacs Emacs/27.1 (TTY; x86_64-pc-linux-gnu)", "URL/Emacs Emacs/26.3 (TTY; x86_64-apple-darwin18.2.0)"]

        geodb = "GeoLite2-Country.mmdb"
        
        try:
            self.geodb_reader = geoip2.database.Reader(os.path.join(os.path.dirname(__file__),geodb))
        except FileNotFoundError:
            self.geodb_reader = None
            # print("Please add GeoLite2-Country.mmdb in %s to have Country mapping support" % (os.path.dirname(__file__)))

    def reset_virtualpackets(self):
        self.virtual_packets = []
        
    def get_virtualpackets(self):
        return self.virtual_packets

    def add_virtualpacket(self, layer, protocol, flow, ip_src, ip_dst, port_src, port_dst, packet_size=None, frame_time=None):
        vp = VirtualPacket()
        vp.build(layer, protocol, flow, ip_src, ip_dst, port_src, port_dst, packet_size, frame_time)
        self.virtual_packets.append(vp)
        
    def set_service(self, service):
        self.service = service
        
    def set_vardict(self, vardict):
        self.vardict = vardict
        
    def get_random_client_ip(self):
        return utils.getRandomIP("192.168.0.0/16", ipfail="172.16.42.42").get()

    def get_random_server_ip(self):
        return utils.getRandomIP("10.0.0.0/8", ipfail="10.1.2.42").get()

    def get_random_ephemeral_port(self):
        return str(random.randint(4096, 65534))
    
    def get_mand_variable(self, varname):
        return self.vardict[varname]

    def gen_uuid_fixed(self, event, value):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, value))

    def gen_uuid(self, event):
        return str(uuid.uuid4())

    def gen_md5(self):
        return hashlib.md5(bytes(str(random.randint(1, 99999999999)), "utf8")).hexdigest()
    
    def gen_sha1(self):
        return hashlib.sha1(bytes(str(random.randint(1, 99999999999)), "utf8")).hexdigest()

    def gen_sha256(self):
        return hashlib.sha256(bytes(str(random.randint(1, 99999999999)), "utf8")).hexdigest()

    def gen_string(self, length):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k = length))
    
    def get_consistent_id(self, name, idlen):
        consistent_id = int(hashlib.sha256(bytes(name, "utf8")).hexdigest(), 16)
        return str(consistent_id)[:idlen]

    def get_random_user_agent(self):
        random_useragent = random.randint(0, len(self.user_agents)-1)
        return self.user_agents[random_useragent]

    def get_country_for_ip(self, ip):        
        try:
            response = self.geodb_reader.country(ip)
            return response.country.names["en"]
        except:
            return "Internal Networks"

    def set_variable_if_generated(self, event, variable, value):
        try:
            if variable in event["generated_variables"]:
                event["variables"][variable] = value
        except:
            pass

    def set_variables_if_generated(self, event, variables):
        for v in variables:
            self.set_variable_if_generated(event, v, self.get_variable(v))

    def populate_variables(self, event, variables):
        for v in variables:
            if v not in event["variables"]:
                event["variables"][v] = self.get_variable(v)

    def get_consistent_macaddr(self, ip):
        ipn = int(ipaddress.IPv4Address("192.168.45.43"))
        ipnhex = format(ipn, "X")
        extrahex = ipn >> 18
        extrahex = format(extrahex, "X")

        macstr = ""

        for index in range(0, len(extrahex), 2):
            macstr += str(extrahex[index:index+2])
            macstr += ":"

        for index in range(0, len(ipnhex), 2):
            macstr += str(ipnhex[index:index+2])
            if index + 2 < len(ipnhex):
                macstr += ":"
        return macstr
                
    def get_variable(self, varname):
        got_default = False
        retval = ""
        try:
            try:
                return self.vardict[varname]
            except:
                return self.built_variables[varname]
        except:
            if varname == "$ip-src":
                got_default = True
                retval = self.get_random_client_ip()
            if varname == "$ip-dst":
                got_default = True
                retval = self.get_random_server_ip()
            if varname == "$port-src":
                got_default = True
                retval = self.get_random_ephemeral_port()
            if varname == "$resolver":
                got_default = True
                retval = "1.1.1.1"
            if varname == "$port-dst":
                got_default = True
                if self.service == "dns":
                    retval = "53"
                elif self.service == "http":
                    retval = "80"
                elif self.service == "https":
                    retval = "443"
                else:
                    retval = "80"
            if varname == "$protocol":
                got_default = True
                retval = "tcp"
                if self.service == "dns":
                    retval = "udp"
            
            if varname == "$method":
                got_default = True
                retval = "GET"
            if varname == "$user-agent":
                got_default = True
                retval = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Pcraft/0.0.7"
            if varname == "$uri":
                got_default = True
                retval = "/"
            if varname == "$resp-httpver":
                got_default = True
                retval = "HTTP/1.1"
            if varname == "$resp-code":
                got_default = True
                retval = "200 OK"
            if varname == "$resp-server":
                got_default = True
                retval = "nginx"
            if varname == "$resp-content-type":
                got_default = True
                retval = "text/html"
            if varname == "$resp-content":
                got_default = True
                retval = "<html><body>Hello, you!</body></html>"

        if got_default:
            self.built_variables[varname] = retval
            return retval

        return None
    
