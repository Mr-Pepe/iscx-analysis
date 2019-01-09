import pickle
import os
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm
import re

# Set console width
desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)

p_files_path = "../datasets/all_flows_save"

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

all_flows = []
flows_by_app = {key: set() for key in app_names}
labels = []
i_file = 0

for dirpath, dirnames, filenames in os.walk(p_files_path):

    for filename in filenames:
        path = os.path.join(dirpath, filename)

        # Look at non-vpn and non-tor files
        # if filename.find('vpn') == -
        if True:
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

                for flow in flows:
                    # Discard IP addresses
                    flow = flow[2:]
                    flows_by_app[app_name].add(flow)

                i_file += 1


# Reduce the all_flows_save to a set for each app and then look at the overall set again
n_flows = 0
all_flows = set()
for app, flows in flows_by_app.items():
    n_flows += len(flows)

    for flow in flows:
        all_flows.add(flow)

print("%d all_flows_save can be associated with a specific application" %len(all_flows))
print("%d all_flows_save are associated with more than one app" % (n_flows-len(all_flows)))

## Calculate the overlap between apps
# Create array with zeros on the main diagonal and ones elsewhere
overlap = np.zeros((len(app_names), len(app_names)),dtype='int')
overlap_by_app = {key: 0 for key in app_names}
overlapping_flows_by_app = {key: set() for key in app_names}


for i_app1, app1 in enumerate(app_names):
    for i_app2, app2 in enumerate(app_names):
        if i_app1 != i_app2:
            overlapping_flows = flows_by_app[app1] & flows_by_app[app2]
            overlap[i_app1, i_app2] = len(overlapping_flows)

            for flow in overlapping_flows:
                overlapping_flows_by_app[app1].add(flow)


for app in app_names:
    overlap_by_app[app] = len(overlapping_flows_by_app[app]) / len(flows_by_app[app])




overlap[overlap > 6000] = 6000

df = pd.DataFrame(overlap, columns=app_names)

sns.heatmap(df)
plt.show()

print("Test")






# df = {'label': labels,
#       'sip': [flow[0] for flow in all_flows],
#       'dip': [flow[1] for flow in all_flows],
#       'sport': [flow[2] for flow in all_flows],
#       'dport': [flow[3] for flow in all_flows],
#       'prot': [flow[4] for flow in all_flows]
#       }
#
# df = pd.DataFrame(df)
# df = df[['label', 'sip', 'dip', 'sport', 'dport', 'prot']]
#
# reduced_df = df[['sport', 'dport', 'prot']]
