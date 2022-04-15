# Analysis of the ISCX VPN-nonVPN Dataset 2016 for Encrypted Network Traffic Classification

Already half of today’s internet traffic is encrypted using protocols like SSL/TLS.
This prevents classic deep packet inspection approaches from analyzing packet payloads.
Recently, researchers published a deep learning approach, claiming that their trained
model is capable of finding patterns in encrypted network traffic payloads and classifying
applications based on these patterns. This work shows that the claim is unlikely to be true,
because the utilized dataset exposes features that allow for highly accurate classification
without incoporating any payload data.


Find further information in report.pdf.

## Procedure
1. Download .pcap-files of the ISCX VPN-nonVPN Dataset 2016 from [here](https://www.unb.ca/cic/datasets/vpn.html).
2. Run extract_flows_from_pcap.py on the downloaded .pcap-files
3. Run analyze_flows.py on the extracted flows

The code has been tested with Python 3.10 and the dependencies from the `requirements.txt` file.


