import os
import pickle

from scapy.all import *

pcap_path = "./datasets/pcaps"
save_dir_path = "../datasets/flows"


paths = []
filenames = []

pat = re.compile("[^\.]*\.")

for dirpath, dirnames, filenames in os.walk(pcap_path):

    n_files = len(filenames)
    i_file = 0

    for filename in filenames:

        i_file += 1

        path = os.path.join(dirpath, filename)

        actual_name = pat.match(filename)

        save_path = os.path.join(
            save_dir_path,
            filename[actual_name.span()[0] : actual_name.span()[1] - 1] + "_flows.p",
        )

        if not os.path.isfile(save_path):
            print("Loading file %d/%d: %s" % (i_file, n_files, path))

            flow_keys = set()
            i_packet = 0
            flows = {}

            ## The following code is taking from the scapy sniff function
            sniff_sockets = {}
            sniff_sockets[PcapReader(path)] = path
            _main_socket = next(iter(sniff_sockets))
            select_func = _main_socket.select
            if not all(select_func == sock.select for sock in sniff_sockets):
                warning(
                    "Warning: inconsistent socket types ! The used select function"
                    "will be the one of the first socket"
                )
            _select = lambda sockets, remain: select_func(sockets, remain)[0]
            remain = None

            try:
                while sniff_sockets:
                    for s in _select(sniff_sockets, remain):
                        try:
                            packet = s.recv()
                        except socket.error as ex:
                            log_runtime.warning(
                                "Socket %s failed with '%s' and thus"
                                " will be ignored" % (s, ex)
                            )
                            del sniff_sockets[s]
                            continue
                        if packet is None:
                            try:
                                if s.promisc:
                                    continue
                            except AttributeError:
                                pass
                            del sniff_sockets[s]
                            break

                        i_packet += 1
                        if (i_packet % 10000) == 0:
                            print("Loading packet %d" % i_packet)

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
                            # Skip if no payload
                            if getattr(packet[TCP], "load", 0) == 0:
                                continue
                            sport = packet[TCP].sport
                            dport = packet[TCP].dport
                            prot = "TCP"
                        elif packet.haslayer(UDP):
                            if packet.haslayer(DNS):
                                pass
                                # dns_names.append(packet[4].qname.decode())
                            else:
                                sport = packet[UDP].sport
                                dport = packet[UDP].dport
                                prot = "UDP"

                        if (
                            sip is None
                            or dip is None
                            or sport is None
                            or dport is None
                            or prot is None
                        ):
                            pass
                        else:
                            flow_key = (sip, dip, sport, dport, prot)
                            flow_keys.add(flow_key)

                            if not flow_key in flows:
                                flows[flow_key] = 0

                            flows[flow_key] += 1

            except KeyboardInterrupt:
                pass

            for s in sniff_sockets:
                s.close()

            print("Number of unique flows: %d" % len(flow_keys))

            with open(save_path, "wb") as file:
                pickle.dump(flows, file)
