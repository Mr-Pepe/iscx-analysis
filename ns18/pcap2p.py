from scapy.all import *
import pickle
import os


pcap_path = "../datasets/pcaps"
save_dir_path = "../datasets/p_files"


paths = []
filenames = []
for dirpath, dirnames, filenames in os.walk(pcap_path):
    for filename in filenames:

        try:
            path = os.path.join(dirpath, filename)
            save_path = os.path.join(save_dir_path, filename+'.p')

            if not os.path.isfile(save_path):

                print("Reading %s" %path)
                packets = rdpcap(path)

                with open(save_path, 'wb') as file:
                    pickle.dump(packets, file)

                del packets
        except Exception:
            print("Unable to read in %s" % path)
            print(Exception)

#     for packet in packets:
#         try:
#             # print("%d    %d   %d" % (packet[TCP].sport, packet[TCP].dport, packet[TCP].ack))
#             sports.append(packet[TCP].sport)
#             dports.append(packet[TCP].dport)
#             flows.append((packet[IP].src, packet[IP].dst, packet[TCP].sport, packet[TCP].dport))
#
#         except:
#             pass
#
sports = set(sports)
dports = set(dports)
#
# print("Test")
