import numpy as np
import pandas as pd
import os
os.chdir('/home/vasste/ml')
from telecom.train_columns import *
os.chdir('/home/vasste/mlbootcap/TelecomDataCup/dataset')

c = pd.read_pickle('train/subs_csi_train.pk')
f = pd.read_pickle('train/subs_features_train.pk')
f['COM_CAT#34'] = f['COM_CAT#34'].fillna(f.describe()['COM_CAT#34']['75%'], axis=0)
f['COM_CAT#34'] = f['COM_CAT#34'].astype(int)

f = f.join(c)
target = 'CSI'
df = f
feature = 'COM_CAT#34'
for i in ['COM_CAT#1', 'COM_CAT#34', 'COM_CAT#2', 'COM_CAT#3', 'INTERNET_TYPE_ID', 'DEVICE_TYPE_ID',
         'COM_CAT#25', 'COM_CAT#26', 'ACT']:
    f[i] = f[i].astype('category')
    lst = []
    for i in range(df[feature].nunique()):
        val = list(df[feature].unique())[i]
        lst.append([feature,                                                        # Variable
                    val,                                                            # Value
                    df[df[feature] == val].count()[feature],                        # All
                    df[(df[feature] == val) & (df[target] == 0)].count()[feature],  # Good (think: Fraud == 0)
                    df[(df[feature] == val) & (df[target] == 1)].count()[feature]]) # Bad (think: Fraud == 1)

        data = pd.DataFrame(lst, columns=['Variable', 'Value', 'All', 'Good', 'Bad'])

        data['Share'] = data['All'] / data['All'].sum()
        data['Bad Rate'] = data['Bad'] / data['All']
        data['Distribution Good'] = (data['All'] - data['Bad']) / (data['All'].sum() - data['Bad'].sum())
        data['Distribution Bad'] = data['Bad'] / data['Bad'].sum()
        data['WoE'] = np.log(data['Distribution Good'] / data['Distribution Bad'])

        data = data.replace({'WoE': {np.inf: 0, -np.inf: 0}})

        data['IV'] = data['WoE'] * (data['Distribution Good'] - data['Distribution Bad'])

        data = data.sort_values(by=['Variable', 'Value'], ascending=[True, True])
        data.index = range(len(data.index))
    print(data)




import numpy as np
import pandas as pd
import os
os.chdir('/home/vasste/ml')
from telecom.train_columns import *
os.chdir('/home/vasste/mlbootcap/TelecomDataCup/dataset')

f = pd.read_pickle('train/subs_features_train.pk')
c = pd.read_pickle('train/subs_csi_train.pk')
for i in ['1', '2', '3', '34', '8']:
    for j in ['32', '33', '17']:
        f['COM_CAT#' + i + j] = f['COM_CAT#' + i] * f['COM_CAT#' + j]

for i in ['ARPU_GROUP', 'RENT_CHANNEL', 'ITC', 'VAS']:
    for j in ['32', '33', '17', '22', '28']:
        f[i + '#' + j] = f[i] * f['COM_CAT#' + j]
f = f.join(c)
f['INTERNET_TYPE_ID']
f = f.reindex(['CSI'] + list([a for a in f.columns if a != 'CSI']), axis=1)
f = pd.get_dummies(f, columns=['BASE_TYPE','ACT', 'COM_CAT#26'])
f.corr().style.background_gradient()