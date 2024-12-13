# MPLS SDN Networking Project

## Overview
This project is a class assignment for a Networking course, designed to demonstrate the implementation of Multi-Protocol Label Switching (MPLS) using Software-Defined Networking (SDN) principles. The goal is to provide a simple, educational implementation of MPLS routing without relying on external MPLS modules.

## Project Purpose
- Understand MPLS routing mechanisms
- Implement MPLS label switching in a Software-Defined Network
- Demonstrate label push, swap, and pop operations
- Learn SDN controller programming with Ryu

## Network Topology
```
h1 --- s1 --- s2 (Edge LSR 1) --- s3 (Core LSR 1) --- s4 (Core LSR 2) --- s5 (Edge LSR 2) --- s6 --- h2
```

### Topology Details
- **Total Switches**: 6 switches
- **Switches Types**:
  - 2 Simple Switches (s1, s6)
  - 2 Edge Label Switching Routers (LSR) (s2, s5)
  - 2 Core Label Switching Routers (LSR) (s3, s4)
- **Hosts**: 
  - h1 (IP: 10.0.0.1/24)
  - h2 (IP: 10.0.0.2/24)

## MPLS Label Configuration
### Label Mapping
- **h1 to h2 Path**:
  - Ingress Label (Edge LSR 1): 16
  - Middle Label (Core LSR 1): 32
  - Middle Label (Core LSR 2): 64
  - Egress Label (Edge LSR 2): Removed

- **h2 to h1 Path**:
  - Ingress Label (Edge LSR 2): 100
  - Middle Label (Core LSR 2): 200
  - Middle Label (Core LSR 1): 300
  - Egress Label (Edge LSR 1): Removed

### MPLS Label Assignment

The Ryu controller assigns the following MPLS labels:

| Direction  | Input Label | Middle Label | Output Label |
|-------------|-------------|--------------|-------------|
| h1 to h2    | 16          | 32           | 64          |
| h2 to h1    | 100         | 200          | 300         |

## MPLS Operations
1. **Push**: Add an MPLS label at the ingress edge router
2. **Swap**: Replace existing MPLS label with a new label at intermediate routers
3. **Pop**: Remove MPLS label at the egress edge router to forward to the final destination

## Controller Initialization
The Ryu SDN controller initializes each switch with specific MPLS rules:
- Edge LSRs: Responsible for pushing and popping MPLS labels
- Core LSRs: Perform label swapping based on incoming labels

## Prerequisites
- Mininet
- Ryu SDN Framework
- Python 3.x
- OpenFlow 1.3

## Installation Steps
1. Clone the repository
```bash
git clone https://github.com/Youneskr/MPLS-SDN-Networking-Project.git
cd mpls-sdn-project
```

2. Install dependencies
```bash
pip install ryu mininet
```
## Ryu Controller Configuration

The `mpls_controller.py` script uses the Ryu controller to implement the MPLS forwarding rules. The controller installs the necessary flow entries in each switch to perform push, swap, and pop label operations based on the defined MPLS labels and packet destination IP addresses. Each switch is initialized with the corresponding flow entry.

## Running the Project

1.  **Start the controller:** Run `ryu-manager mpls_controller.py` in one terminal.

2.  **Start the Mininet topology:** In another terminal, run `python mpls_topo.py`.  This will start the Mininet network.

3.  **Access Mininet CLI:** The Mininet command-line interface will be available to test the network.

4.  **Test the network:** Use the `ping` command to test connectivity between `h1` and `h2`. For example: `h1 ping h2`.

5.  **Wireshark Capture:** Capture network

## Limitations
- Simplified MPLS implementation
- Limited to specific network topology
- Educational purposes only

## Contributing
Contributions, issues, and feature requests are welcome!

## License
[Specify your license]

## Acknowledgments
- Networking Class Project
- Ryu SDN Framework
- Mininet Network Emulator
