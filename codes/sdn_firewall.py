from pox.core import core
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.ethernet import ethernet
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr

log = core.getLogger()

BLOCK_RULES = [
    ("10.0.0.1", "10.0.0.3"),
    ("10.0.0.3", "10.0.0.1"),
]

class SDNFirewall(object):

    def __init__(self):
        core.openflow.addListeners(self)
        log.info("SDN Firewall Controller Started")
        log.info("Blocking h1(10.0.0.1) <-> h3(10.0.0.3)")

    def _handle_ConnectionUp(self, event):
        log.info("Switch connected: %s", event.dpid)
        for (src_ip, dst_ip) in BLOCK_RULES:
            msg = of.ofp_flow_mod()
            msg.priority = 20
            msg.match.dl_type = ethernet.IP_TYPE
            msg.match.nw_src = IPAddr(src_ip)
            msg.match.nw_dst = IPAddr(dst_ip)
            event.connection.send(msg)
            log.info("DROP rule installed: %s -> %s", src_ip, dst_ip)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return
        ip_pkt = packet.find('ipv4')
        if ip_pkt is None:
            return
        src = str(ip_pkt.srcip)
        dst = str(ip_pkt.dstip)
        for (rule_src, rule_dst) in BLOCK_RULES:
            if src == rule_src and dst == rule_dst:
                log.warning("BLOCKED PACKET: %s -> %s", src, dst)
                return

def launch():
    core.registerNew(SDNFirewall)

