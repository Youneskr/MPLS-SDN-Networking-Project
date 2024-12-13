from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, mpls, ipv4
from ryu.lib import mac
from ryu.lib.packet import ether_types

class MPLSController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MPLSController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.mpls_labels = {
            'h1_to_h2': {'in_label': 16, 'middle_label': 32, 'out_label': 64},
            'h2_to_h1': {'in_label': 100, 'middle_label': 200, 'out_label': 300},
        }
        self.switch_name = {
            1: "s1",  # Simple Switch
            2: "Edge_LSR_1",
            3: "Core_LSR_1",
            4: "Core_LSR_2",
            5: "Edge_LSR_2",
            6: "s6"  # Simple Switch
        }
        self.logger.info("\n*** MPLS Controller Started!\n")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        try:
            switch_name = self.switch_name[dpid]
        except KeyError:
            self.logger.error(f"Unknown datapath ID: {dpid}")
            return

        # self.logger.info(f"Switch connected: {switch_name}")

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        if dpid == 2:  # Edge LSR 1
            self.configure_edge_lsr1(datapath, parser)
        elif dpid == 3:  # Core LSR 1
            self.configure_core_lsr1(datapath, parser)
        elif dpid == 4:  # Core LSR 2
            self.configure_core_lsr2(datapath, parser)
        elif dpid == 5:  # Edge LSR 2
            self.configure_edge_lsr2(datapath, parser)
        elif dpid in [1, 6]:  # Simple switches - basic flooding
            pass


    def configure_edge_lsr1(self, datapath, parser):
        self.logger.info("Configuring Edge LSR 1")
        # Push MPLS label for h1->h2
        match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.2')
        actions = [
            parser.OFPActionPushMpls(ethertype=34887),
            parser.OFPActionSetField(mpls_label=self.mpls_labels['h1_to_h2']['in_label']),
            parser.OFPActionOutput(2)
        ]
        self.add_flow(datapath, 1, match, actions)
        # Pop MPLS label for h2->h1
        match = parser.OFPMatch(eth_type=34887, mpls_label=self.mpls_labels['h2_to_h1']['out_label'])
        actions = [
            parser.OFPActionPopMpls(ethertype=0x0800),
            parser.OFPActionOutput(1)
        ]
        self.add_flow(datapath, 1, match, actions)

    def configure_core_lsr1(self, datapath, parser):
        self.logger.info("Configuring Core LSR 1")
        # Swap MPLS label for h1->h2
        match = parser.OFPMatch(eth_type=34887, mpls_label=self.mpls_labels['h1_to_h2']['in_label'])
        actions = [
            parser.OFPActionPopMpls(),
            parser.OFPActionPushMpls(ethertype=34887),
            parser.OFPActionSetField(mpls_label=self.mpls_labels['h1_to_h2']['middle_label']),
            parser.OFPActionOutput(2)
        ]
        self.add_flow(datapath, 1, match, actions)
        # Swap MPLS label for h2->h1
        match = parser.OFPMatch(eth_type=34887, mpls_label=self.mpls_labels['h2_to_h1']['middle_label'])
        actions = [
            parser.OFPActionPopMpls(),
            parser.OFPActionPushMpls(ethertype=34887),
            parser.OFPActionSetField(mpls_label=self.mpls_labels['h2_to_h1']['out_label']),
            parser.OFPActionOutput(1)
        ]
        self.add_flow(datapath, 1, match, actions)

    def configure_core_lsr2(self, datapath, parser):
        self.logger.info("Configuring Core LSR 2")
        # Swap MPLS label for h1->h2
        match = parser.OFPMatch(eth_type=34887, mpls_label=self.mpls_labels['h1_to_h2']['middle_label'])
        actions = [
            parser.OFPActionPopMpls(),
            parser.OFPActionPushMpls(ethertype=34887),
            parser.OFPActionSetField(mpls_label=self.mpls_labels['h1_to_h2']['out_label']),
            parser.OFPActionOutput(2)
        ]
        self.add_flow(datapath, 1, match, actions)
        # Swap MPLS label for h2->h1
        match = parser.OFPMatch(eth_type=34887, mpls_label=self.mpls_labels['h2_to_h1']['in_label'])
        actions = [
            parser.OFPActionPopMpls(),
            parser.OFPActionPushMpls(ethertype=34887),
            parser.OFPActionSetField(mpls_label=self.mpls_labels['h2_to_h1']['middle_label']),
            parser.OFPActionOutput(1)
        ]
        self.add_flow(datapath, 1, match, actions)

    def configure_edge_lsr2(self, datapath, parser):
        self.logger.info("Configuring Edge LSR 2")
        # Pop MPLS label for h1->h2
        match = parser.OFPMatch(eth_type=34887, mpls_label=self.mpls_labels['h1_to_h2']['out_label'])
        actions = [
            parser.OFPActionPopMpls(ethertype=0x0800),
            parser.OFPActionOutput(2)
        ]
        self.add_flow(datapath, 1, match, actions)
        # Push MPLS label for h2->h1
        match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.1')
        actions = [
            parser.OFPActionPushMpls(ethertype=34887),
            parser.OFPActionSetField(mpls_label=self.mpls_labels['h2_to_h1']['in_label']),
            parser.OFPActionOutput(1)
        ]
        self.add_flow(datapath, 1, match, actions)


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        
        try:
            switch_name = self.switch_name[datapath.id]
            self.logger.info(f"\n\n*** Flow added to {switch_name}:\n*** Match: {match}\n*** Actions: {actions}\n\n")
        except KeyError:
            self.logger.error(f"Could not get switch name for datapath ID: {datapath.id}")
        
        datapath.send_msg(mod)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes", ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        
        # if datapath.id in [1, 5]:

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        # self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        if datapath.id == 1 or datapath.id == 6:
            # install a flow to avoid packet_in next time
            if out_port != ofproto.OFPP_FLOOD:
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)