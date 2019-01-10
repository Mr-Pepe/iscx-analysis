import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Qt5Agg')
# Set console width
desired_width = 320
np.set_printoptions(linewidth=desired_width)

p_files_path = "../datasets/all_flows_with_packets"

# Order is important because 'tor' is included in 'torrent' and tor filenames also include other app names
app_names = ['torrent',
             'tor',
             'aim',
             'email',
             'facebook',
             'ftps',
             'gmail',
             'hangout',
             'icq',
             'netflix',
             'scp',
             'sftp',
             'skype',
             'spotify',
             'voipbuster',
             'vimeo',
             'youtube']

flows_by_app = {key: {} for key in app_names}
labels = []
i_file = 0

use_vpn = True

for dirpath, dirnames, filenames in os.walk(p_files_path):

    for filename in filenames:
        path = os.path.join(dirpath, filename)

        # Look at non-vpn and non-tor files
        if use_vpn or filename.find('vpn') == -1:
            found = 0
            app_name = ''
            # Organize by application
            for app in app_names:
                if filename.lower().find(app) != -1:
                    found += 1
                    app_name = app
                    break

            if found == 0:
                print("Could not find corresponding app")
            if found == 2:
                print("Found to corresponding apps")

            with open(path, 'rb') as file:
                flows = pickle.load(file)

                for flow, n_packets in flows.items():
                    # Discard IP addresses
                    flow = flow[2:]

                    if flow not in flows_by_app[app_name]:
                        flows_by_app[app_name][flow] = 0

                    flows_by_app[app_name][flow] += n_packets

                i_file += 1

# Calculate the flow overlap between apps
n_overlapping_flows = np.zeros((len(app_names), len(app_names)), dtype='int')
n_ambiguous_packets = np.zeros((len(app_names), len(app_names)), dtype='int')
# Which flows in an app are also used in another app
overlapping_flows_by_app = {key: {} for key in app_names}

for i_app1, app1 in enumerate(app_names):
    for i_app2, app2 in enumerate(app_names):
        if i_app1 != i_app2:
            overlapping_flows = set(flows_by_app[app1].keys()) & set(flows_by_app[app2].keys())
            n_overlapping_flows[i_app1, i_app2] = len(overlapping_flows)

            for flow in overlapping_flows:
                overlapping_flows_by_app[app1][flow] = flows_by_app[app1][flow]

# Percentage of flows in an app also used in another app
unique_flows_by_app = {key: 0 for key in app_names}
# Percentage of packets recorded for an app that can be clearly associated with it
unambiguous_packets_by_app = {key: 0 for key in app_names}

n_flows_total   = 0
n_packets_total  = 0
n_unique_flows_total = 0
n_unambiguous_packets_total = 0

for app in app_names:
    # Calculate percentage of unique flows
    n_flows_this_app            = len(flows_by_app[app])
    n_non_unique_flows_this_app = len(overlapping_flows_by_app[app])
    n_unique_flows_this_app     = n_flows_this_app - n_non_unique_flows_this_app
    flow_overlap_this_app       = n_unique_flows_this_app / n_flows_this_app

    # Calculate percentage of unambiguous packets
    n_packets_this_app              = sum(list(flows_by_app[app].values()))
    n_ambiguous_packets_this_app    = sum(list(overlapping_flows_by_app[app].values()))
    n_unambiguous_packets_this_app  = n_packets_this_app - n_ambiguous_packets_this_app
    unambiguous_packets_this_app    = n_unambiguous_packets_this_app / n_packets_this_app

    unambiguous_packets_by_app[app] = unambiguous_packets_this_app
    unique_flows_by_app[app]        = flow_overlap_this_app

    n_flows_total += n_flows_this_app
    n_packets_total += n_packets_this_app
    n_unique_flows_total += n_unique_flows_this_app
    n_unambiguous_packets_total += n_unambiguous_packets_this_app

print("%f%% of all flows can be associated with a specific application" % (n_unique_flows_total / n_flows_total))
print("%f%% of all packets can be associated with a specific application" % (n_unambiguous_packets_total / n_packets_total))

table_content = np.empty((18, 5), dtype='object')
col_labels = ("Application", "Number of flows", "Number of packets", "Unique flows", "Unambiguous packets")
table_content[:, 0]      = np.array([app_names + ["Total"]])[0]
table_content[:-1, 1]    = np.array([len(flows) for app, flows in flows_by_app.items()])
table_content[-1, 1]     = table_content[:-1, 1].sum()
table_content[:-1, 2]    = np.array([sum(list(flows.values())) for flows in list(flows_by_app.values())])
table_content[-1, 2]     = table_content[:-1, 2].sum()
table_content[:-1, 3]    = np.array(list(unique_flows_by_app.values())).round(decimals=2)
table_content[-1, 3]     = np.round(n_unique_flows_total / n_flows_total, decimals=2)
table_content[:-1, 4]    = np.array(list(unambiguous_packets_by_app.values())).round(decimals=2)
table_content[-1, 4]     = np.round(n_unambiguous_packets_total / n_packets_total, decimals=2)

fig = plt.figure()
ax = plt.gca()
the_table = ax.table(cellText=table_content, colLabels=col_labels, loc='center')
table_props = the_table.properties
the_table.auto_set_font_size(False)
the_table.set_fontsize(16)

plt.show()
