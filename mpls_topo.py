from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def create_mpls_topo():
    """
    h1 --- s1 --- s2 (Edge LSR 1) --- s3 (Core LSR 1) --- s4 (Core LSR 2) --- s5 (Edge LSR 2) --- s6 --- h2
    """
    
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch, link=TCLink)

    print("*** Add controller...")
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    print("*** Add switches...")
    s1 = net.addSwitch('s1')  # Simple switch
    s2 = net.addSwitch('s2')  # Edge LSR 1
    s3 = net.addSwitch('s3')  # Core LSR 1
    s4 = net.addSwitch('s4')  # Core LSR 2
    s5 = net.addSwitch('s5')  # Edge LSR 2
    s6 = net.addSwitch('s6')  # Simple switch

    print("*** Add hosts...")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')

    print("*** Add links...")
    net.addLink(h1, s1)
    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s3, s4)
    net.addLink(s4, s5)
    net.addLink(s5, s6)
    net.addLink(s6, h2)

    print("*** Build network...")
    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    s4.start([c0])
    s5.start([c0])
    s6.start([c0])

    return net

if __name__ == '__main__':
    setLogLevel('info')
    net = create_mpls_topo()
    CLI(net)
    net.stop()
