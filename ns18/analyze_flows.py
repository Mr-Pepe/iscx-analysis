import pickle
from pathlib import Path
from typing import Counter

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Qt5Agg")
# Set console width
desired_width = 320
np.set_printoptions(linewidth=desired_width)

flow_files_path = Path("./datasets/flows")

# Order is important because 'tor' is included in 'torrent' and tor filenames also include other app names
app_names = [
    "torrent",
    "tor",
    "aim",
    "email",
    "facebook",
    "ftps",
    "gmail",
    "hangout",
    "icq",
    "netflix",
    "scp",
    "sftp",
    "skype",
    "spotify",
    "voipbuster",
    "vimeo",
    "youtube",
]

flows_by_app = {app: {} for app in app_names}
labels = []

use_vpn = True

for flow_file in flow_files_path.glob("*.p"):

    if use_vpn or "vpn" not in flow_file.stem:
        app_name = ""
        # Organize by application
        for app in app_names:
            if app in flow_file.stem.lower():
                app_name = app
                break

        with open(flow_file, "rb") as file:
            flows: Counter = pickle.load(file)

            for flow, n_packets in flows.items():
                # Discard IP addresses
                flow = flow[2:]

                if flow not in flows_by_app[app_name]:
                    flows_by_app[app_name][flow] = 0

                flows_by_app[app_name][flow] += n_packets

# Calculate the flow overlap between apps
n_overlapping_flows = np.zeros((len(app_names), len(app_names)), dtype="int")
n_ambiguous_packets = np.zeros((len(app_names), len(app_names)), dtype="int")
# Which flows in an app are also used in another app
overlapping_flows_by_app = {key: {} for key in app_names}

for i_app1, app1 in enumerate(app_names):
    for i_app2, app2 in enumerate(app_names):
        if i_app1 != i_app2:
            overlapping_flows = set(flows_by_app[app1].keys()) & set(
                flows_by_app[app2].keys()
            )
            n_overlapping_flows[i_app1, i_app2] = len(overlapping_flows)

            for flow in overlapping_flows:
                overlapping_flows_by_app[app1][flow] = flows_by_app[app1][flow]

# Percentage of flows in an app also used in another app
unique_flows_by_app = {key: 0 for key in app_names}
# Percentage of packets recorded for an app that can be clearly associated with it
unambiguous_packets_by_app = {key: 0 for key in app_names}

n_flows_total = 0
n_packets_total = 0
n_unique_flows_total = 0
n_unambiguous_packets_total = 0

for app in app_names:
    # Calculate percentage of unique flows
    n_flows_this_app = len(flows_by_app[app])
    n_non_unique_flows_this_app = len(overlapping_flows_by_app[app])
    n_unique_flows_this_app = n_flows_this_app - n_non_unique_flows_this_app
    flow_overlap_this_app = n_unique_flows_this_app / n_flows_this_app

    # Calculate percentage of unambiguous packets
    n_packets_this_app = sum(list(flows_by_app[app].values()))
    n_ambiguous_packets_this_app = sum(list(overlapping_flows_by_app[app].values()))
    n_unambiguous_packets_this_app = n_packets_this_app - n_ambiguous_packets_this_app
    unambiguous_packets_this_app = n_unambiguous_packets_this_app / n_packets_this_app

    unambiguous_packets_by_app[app] = unambiguous_packets_this_app
    unique_flows_by_app[app] = flow_overlap_this_app

    n_flows_total += n_flows_this_app
    n_packets_total += n_packets_this_app
    n_unique_flows_total += n_unique_flows_this_app
    n_unambiguous_packets_total += n_unambiguous_packets_this_app

print(
    f"{n_unique_flows_total / n_flows_total:.2f}% of all flows can be associated "
    "with a specific application"
)
print(
    f"{n_unambiguous_packets_total / n_packets_total:.2f}% of all packets can be "
    "associated with a specific application"
)

name_mapping = {
    "AIM chat": "aim",
    "Email": "email",
    "Facebook": "facebook",
    "FTPS": "ftps",
    "Gmail": "gmail",
    "Hangouts": "hangout",
    "ICQ": "icq",
    "Netflix": "netflix",
    "SCP": "scp",
    "SFTP": "sftp",
    "Skype": "skype",
    "Spotify": "spotify",
    "Torrent": "torrent",
    "Tor": "tor",
    "VoipBuster": "voipbuster",
    "Vimeo": "vimeo",
    "Youtube": "youtube",
}

col_labels = (
    "Application",
    "Number of flows",
    "Number of packets",
    "Unique flows",
    "Unambiguous packets",
)
table_content = np.empty((len(app_names) + 1, 5), dtype="object")
table_content[:, 0] = np.array([list(name_mapping.keys()) + ["Total/ Average"]])[0]
table_content[:-1, 1] = np.array(
    [len(flows_by_app[app]) for app in list(name_mapping.values())]
)
table_content[-1, 1] = table_content[:-1, 1].sum()
table_content[:-1, 2] = np.array(
    [sum(list(flows_by_app[app].values())) for app in list(name_mapping.values())]
)
table_content[-1, 2] = table_content[:-1, 2].sum()
table_content[:-1, 3] = np.array(
    [unique_flows_by_app[app] for app in list(name_mapping.values())]
).round(decimals=2)
table_content[-1, 3] = np.round(n_unique_flows_total / n_flows_total, decimals=2)
table_content[:-1, 4] = np.array(
    [unambiguous_packets_by_app[app] for app in list(name_mapping.values())]
).round(decimals=2)
table_content[-1, 4] = np.round(
    n_unambiguous_packets_total / n_packets_total, decimals=2
)


# Use the following lines for a reduced view
# table_content = np.concatenate((np.expand_dims(table_content[:, 0],1), table_content[:, 3:]), axis=1)
# col_labels = ("Application", "Unique flows", "Unambiguous packets")


fig = plt.figure()
ax = plt.gca()
the_table = ax.table(cellText=table_content, colLabels=col_labels, loc="center")
table_props = the_table.properties
the_table.auto_set_font_size(False)
the_table.set_fontsize(16)

plt.show()
