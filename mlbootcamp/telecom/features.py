import numpy as np
import pandas as pd
import datetime
import math
import matplotlib.pyplot as plt
import sklearn.WOEEncoder


def na_and_norm(x):
    return normilize(x.fillna(x.median(axis=0), axis=0))


def normilize(x):
    # MinMax Scaling
    # x = (x - x.min())/(x.max() - x.min())
    # Z
    return (x - x.mean())/x.std()


features_num_cols = ['REVENUE', 'COM_CAT#31', 'COST', 'COM_CAT#23']
features_cat_cols = ['INT_TYPE_2G', 'INT_TYPE_3G', 'INT_TYPE_4G']
feature_columns = features_num_cols + features_cat_cols

for t in ['train']:
    csi = pd.read_pickle('train/subs_csi_' + t + '.pk')
    f = pd.read_pickle('train/subs_features_' + t + '.pk')
    # features = features[feature_columns]

    # feature_cat_desc = features[features_cat_col].describe()
    # for fc in features_cat_col:
    #     features[fc] = features[fc].fillna(feature_cat_desc[fc].top)
    #
    # features_num = features[features_num_col].groupby('SK_ID').mean()
    # features_num = na_and_norm(features_num)
    #
    # binary_columns = [c for c in features_cat_col if feature_cat_desc[c]['unique'] == 2]
    # nonbinary_columns = [c for c in features_cat_col if feature_cat_desc[c]['unique'] > 2]
    #
    # for c in binary_columns[1:]:
    #     top = feature_cat_desc[c]['top']
    #     top_items = features[c] == top
    #     features.loc[top_items, c] = 0
    #     features.loc[np.logical_not(top_items), c] = 1
    #
    # feature_cat = pd.get_dummies(features[features_cat_col]).groupby('SK_ID').sum()
    #
    # sc = datetime.date(2018,11,12)
    # for i in features['COM_CAT#8'].unique():
    #     print(sc - datetime.timedelta(days=int(i)))

    # columns = ['AGE']
    # lack_array = np.empty([csi.index.size, len(columns)])
    # sc = datetime.date(2018,11,12)
    # age = features['COM_CAT#2'].astype('int64')
    # for i,v in enumerate(csi.index):
    #     d = age.loc[v]
    #     md = int(d if type(d) is np.int64 else max(d))
    #     print(sc - datetime.timedelta(days=md))

    # features_cat_uniq = pd.DataFrame(lack_array)
    # features_cat_uniq.index = csi.index
    # features_cat_uniq.columns = columns
    # print(features_cat_uniq)

    #     for c in feature_cat.columns:
    #         if feature_cat.loc[i][c] >= 1:
    #             features_cat_uniq.loc[i][c] = 1
    #
    # features_cat_uniq.to_pickle('features_cat_uniq_' + t + '.pk')

    # features_cat_index = csi.index
    # features_cat_cols = features_cat_cols
    # features_cat_array = np.empty([csi.index.size, len(features_cat_cols)])
    # features_cat_array[:] = 0
    # features_cat = pd.DataFrame(features_cat_array)
    # features_cat.index = features_cat_index
    # features_cat.columns = features_cat_cols
    #
    # # 3 - 2G, 2 - 4G, 1 - 3G
    # g_dic = {'1': ['INT_TYPE_2G'],
    #          '2': ['INT_TYPE_4G'],
    #          '3': ['INT_TYPE_3G']}
    # inet_type = features['INTERNET_TYPE_ID'].groupby('SK_ID').unique()
    # for k in csi.index:
    #     for it in inet_type.loc[k]:
    #         if math.isnan(float(it)):
    #             continue
    #         for cl in g_dic[it]:
    #             features_cat.loc[k][cl] = 1
    #
    # features_cat.to_pickle('train/features_cat_' + t + '.pk')
    fnc = [c for c in f.columns if f[c].dtype.name != 'object']
    fn = f.groupby('SK_ID').mean()[fnc]
    fn = fn.join(csi)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fnc = fnc + ['CSI']
    ax.matshow(fn.corr()[fnc])
    # ticks = np.arange(0, 9, 1)
    # ax.set_xticks(ticks)
    # ax.set_yticks(ticks)
    ax.set_xticklabels(fnc)
    ax.set_yticklabels(fnc)
    plt.show()
    # fn.corr().style.background_gradient()
