import pickle
from scapy.all import *
import os
import re

p_files_path = "../datasets/p_files"
save_dir_path = "../datasets/flows"

paths = []
filenames = []

pat = re.compile('[^\.]*\.')

for dirpath, dirnames, filenames in os.walk(p_files_path):
    for filename in filenames:
        path = os.path.join(dirpath, filename)

        actual_name = pat.match(filename)

        save_path = os.path.join(save_dir_path, filename[actual_name.span()[0]:actual_name.span()[1]-1] + '_flows.p')

        if not os.path.isfile(save_path):

            print("Loading %s" %path)
            with open(path, 'rb') as file:
                packets = pickle.load(file)

                flows = []

                n_packets = len(packets)
                i_packet = 0

                dns_names = []

                for packet in packets:

                    i_packet += 1
                    print("Loading packet %s/%s" %(i_packet, n_packets), flush=True, end='\r')

                    sip = None
                    dip = None
                    sport = None
                    dport = None
                    prot = None

                    if packet.haslayer(IP):
                        sip = packet[IP].src
                        dip = packet[IP].dst
                    if packet.haslayer(IPv6):
                        sip = packet[IPv6].src
                        dip = packet[IPv6].dst

                    if packet.haslayer(TCP):
                        sport = packet[TCP].sport
                        dport = packet[TCP].dport
                        prot = 'TCP'
                    elif packet.haslayer(UDP):
                        if packet.haslayer(DNS):
                            pass
                            # dns_names.append(packet[4].qname.decode())
                        else:
                            sport = packet[UDP].sport
                            dport = packet[UDP].dport
                            prot = 'UDP'

                    if sip is None or dip is None or sport is None or dport is None or prot is None:
                        pass
                    else:
                        flows.append((sip, dip, sport, dport, prot))

                flows = set(flows)

                print("Number of unique flows: %d" % len(flows))

                with open(save_path, 'wb') as file:
                    pickle.dump((flows), file)
