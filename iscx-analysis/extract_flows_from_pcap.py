"""This script counts how many packets belong to each flow in a .pcap file."""

import logging
import pickle
from collections import Counter
from pathlib import Path

from scapy.layers.dns import DNS
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6
from scapy.utils import PcapReader

logger = logging.getLogger(__name__)

pcap_path = Path("./datasets/pcaps")
save_dir_path = Path("./datasets/flows")

for i_pcap_file, pcap_file in enumerate(pcap_path.glob("*.pcap")):

    flows_save_path = save_dir_path / f"{pcap_file.stem}_flows.p"

    # Skip files that have already been processed
    if not flows_save_path.exists():
        print(f"Loading file {i_pcap_file +1}: {pcap_file}")

        # Counts how many packets each flow has
        flow_counter = Counter()

        pcap_reader = PcapReader(str(pcap_file))

        packets = pcap_reader.read_all()

        for packet in packets:

            if packet.haslayer(IP):
                source_ip = packet[IP].src
                destination_ip = packet[IP].dst
            elif packet.haslayer(IPv6):
                source_ip = packet[IPv6].src
                destination_ip = packet[IPv6].dst
            else:
                continue

            if packet.haslayer(TCP):
                # Skip if no payload
                if getattr(packet[TCP], "load", 0) == 0:
                    continue
                source_port = packet[TCP].sport
                destination_port = packet[TCP].dport
                protocol = "TCP"
            elif packet.haslayer(UDP) and not packet.haslayer(DNS):
                source_port = packet[UDP].sport
                destination_port = packet[UDP].dport
                protocol = "UDP"
            else:
                continue

            flow_key = (
                source_ip,
                destination_ip,
                source_port,
                destination_port,
                protocol,
            )
            flow_counter.update((flow_key,))

        print(f"Number of unique flows: {len(flow_counter.keys())}")

        with open(flows_save_path, "wb") as file:
            pickle.dump(flow_counter, file)
