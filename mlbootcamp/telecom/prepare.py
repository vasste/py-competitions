import math
import numpy as np
import pandas as pd
from telecom.train_columns import *


def with_kpi(consumption, kpi_filename):
    kpi = pd.read_pickle(kpi_filename)
    kpi = kpi.fillna(0, axis=0)
    kpi = kpi.groupby('CELL_LAC_ID').mean()
    return consumption.join(kpi, on='CELL_LAC_ID')


def fixesMisses(x, y, dv = np.nan):
    lack_ids_index = y.index.difference(x.index)
    lack_ids_cols = x.columns
    lack_array = np.empty([lack_ids_index.size, len(lack_ids_cols)])
    lack_array[:] = dv
    lack_ids = pd.DataFrame(lack_array)
    lack_ids.index = lack_ids_index
    lack_ids.columns = lack_ids_cols
    return pd.concat([x, lack_ids])


def create_df(df_columns, index):
    lack_array = np.empty([index.size, len(df_columns)])
    lack_array[:] = np.nan
    df = pd.DataFrame(lack_array)
    df.index = index
    df.columns = df_columns
    return df


def na_and_norm(x, csi):
    x = fixesMisses(x, csi)
    return normilize(x.fillna(0, axis=0))


def normilize(x):
    global cat_columns
    # MinMax Scaling
    # return (x - x.min())/(x.max() - x.min())
    # Z
    for cl in x.columns:
        if cl in cat_columns:
            continue
        cl_std = x.std()[cl]
        if not (math.isnan(cl_std) or cl_std == 0):
            x[cl] = (x[cl] - x.mean()[cl]) / cl_std
    return x


def prepare(name, chnn_kpi, chnn_kpi_clst):
    yes_threshold = .3
    csi = pd.read_pickle('train/subs_csi_' + name + '.pk')

    cons = pd.read_pickle('train/subs_bs_consumption_' + name + '.pk')
    sum_mb_min = cons.groupby(['SK_ID', 'CELL_LAC_ID']).agg({'SUM_DATA_MB': 'sum', 'SUM_DATA_MIN': 'sum'})

    avl_columns = ['CELL_AVAILABILITY_2G', 'CELL_AVAILABILITY_3G', 'CELL_AVAILABILITY_4G']
    cells_rate_md_min = sum_mb_min.join(chnn_kpi[avl_columns], on='CELL_LAC_ID')
    cells_rate_md_min = cells_rate_md_min.fillna(0, axis=0)
    for rc in ['2G', '3G', '4G']:
        cells_rate_md_min['RATE_' + rc] = cells_rate_md_min[cells_rate_md_min['CELL_AVAILABILITY_' + rc] > yes_threshold]['SUM_DATA_MB'] / \
                                          cells_rate_md_min[cells_rate_md_min['CELL_AVAILABILITY_' + rc] > yes_threshold]['SUM_DATA_MIN']

    for rc in ['2G', '3G', '4G']:
        cells_rate_md_min['DT_' + rc] = 0
        cells_rate_md_min.loc[cells_rate_md_min['CELL_AVAILABILITY_' + rc] > yes_threshold, 'DT_' + rc] = 1

    cells_rate_md_min = cells_rate_md_min.replace([np.inf, -np.inf], np.nan)
    cells_rate_md_min = cells_rate_md_min.fillna(0, axis=0)
    skid_rate = cells_rate_md_min.groupby('SK_ID').sum()
    skid_rate = skid_rate.drop(avl_columns + ['SUM_DATA_MB', 'SUM_DATA_MIN'], axis=1)
    skid_rate = na_and_norm(skid_rate, csi)

    cons = cons.groupby('SK_ID').mean()
    cons = cons.drop(['CELL_LAC_ID'], axis=1)
    cons = na_and_norm(cons, csi)

    # think to introduce more features
    consumption_kpi = pd.read_pickle('train/subs_bs_consumption_' + name + '_kpi.pk')
    chnn_kpi = consumption_kpi.join(chnn_kpi, on='CELL_LAC_ID')
    chnn_kpi['PSSR_2G_COUNT'] = 0
    chnn_kpi.loc[chnn_kpi['PSSR_2G'] > 0, 'PSSR_2G_COUNT'] = 1
    chnn_kpi['QA'] = np.where(chnn_kpi[avl_columns] > yes_threshold, 1, 0).sum(axis=1)/len(avl_columns)
    chnn_kpi = chnn_kpi.drop(['CELL_LAC_ID'], axis=1)
    chnn_kpi_gb = chnn_kpi.groupby('SK_ID').mean()
    chnn_kpi_gb['QA0'] = 0
    chnn_kpi_gb['QA0'] = chnn_kpi[chnn_kpi['QA'] == 0].groupby(['SK_ID']).count()
    chnn_kpi_gb['QA1'] = 0
    chnn_kpi_gb['QA1'] = chnn_kpi[chnn_kpi['QA'] >= yes_threshold].groupby(['SK_ID']).count()
    chnn_kpi_gb['QA01'] = chnn_kpi_gb['QA0'] / chnn_kpi_gb['QA1']
    chnn_kpi_gb = chnn_kpi_gb.replace([np.inf, -np.inf], np.nan)
    chnn_kpi_gb = na_and_norm(chnn_kpi_gb, csi)

    chnn_kpi_clst_cons = consumption_kpi.join(chnn_kpi_clst, on='CELL_LAC_ID')
    chnn_kpi_clst_cons = chnn_kpi_clst_cons.drop(['CELL_LAC_ID'], axis=1)
    clss = 10
    for i in range(clss):
        chnn_kpi_clst_cons['CLST_' + str(i)] = 0
        chnn_kpi_clst_cons.loc[chnn_kpi_clst_cons['CELL_CLST'] == i, 'CLST_' + str(i)] = 1

    chnn_kpi_clst_cons = chnn_kpi_clst_cons.drop(['CELL_CLST'], axis=1)
    chnn_kpi_clst_cons = chnn_kpi_clst_cons.groupby('SK_ID').mean()
    chnn_kpi_clst_cons = na_and_norm(chnn_kpi_clst_cons, csi)

    data = pd.read_pickle('train/subs_bs_data_session_' + name + '.pk').groupby('SK_ID').mean()
    data = data.drop(['CELL_LAC_ID'], axis=1)
    data = na_and_norm(data, csi)
    voice = pd.read_pickle('train/subs_bs_voice_session_' + name + '.pk').groupby('SK_ID').mean()
    voice = voice.drop(['CELL_LAC_ID'], axis=1)
    voice = na_and_norm(voice, csi)

    features = pd.read_pickle('train/subs_features_' + name + '.pk')
    for i in ['1', '2', '3', '34', '8']:
        for j in ['32', '33', '17', '22', '28']:
            features['COM_CAT#' + i + j] = features['COM_CAT#' + i] * features['COM_CAT#' + j]

    for i in ['ARPU_GROUP', 'RENT_CHANNEL', 'ITC', 'VAS']:
        for j in ['32', '33', '17', '22', '28', '1', '2', '3', '34', '8']:
            features[i + '#' + j] = features[i] * features['COM_CAT#' + j]

    features_num_col = [c for c in features.columns if features[c].dtype.name != 'object']
    features_num = features[features_num_col].groupby('SK_ID').mean()
    features_num = na_and_norm(features_num, csi)

    features['COM_CAT#34'] = features['COM_CAT#34'].fillna(features.describe()['COM_CAT#34']['75%'], axis=0)
    features['COM_CAT#34'] = features['COM_CAT#34'].astype(int)

    features['ARPU_GROUP'] = features['ARPU_GROUP'].fillna(8, axis=0)
    features['ARPU_GROUP'] = features['ARPU_GROUP'].astype(int)
    features['ARPU_GROUPc'] = features['ARPU_GROUP'].astype('category')

    features['COM_CAT#1c'] = features['COM_CAT#1'].astype('category')
    features['COM_CAT#34c'] = features['COM_CAT#34'].astype('category')
    features_cal_col = ['DEVICE_TYPE_ID', 'INTERNET_TYPE_ID', 'COM_CAT#1c', 'COM_CAT#34c', 'ACT', 'BASE_TYPE',
                        'ARPU_GROUPc', 'COM_CAT#7']
    features_cat = pd.get_dummies(features[features_cal_col], columns=features_cal_col)
    features_cat = features_cat.groupby('SK_ID').max()
    features_cat = fixesMisses(features_cat, csi)
    features_cat.fillna(0, axis=0)

    data_clst = fixesMisses(pd.read_pickle('train/subs_bs_data_session_' + name + '_clst.pk'), csi, 0)
    voice_clst = fixesMisses(pd.read_pickle('train/subs_bs_voice_session_' + name + '_clst.pk'), csi, 0)
    cons_cslt = fixesMisses(pd.read_pickle('train/subs_bs_consumption_' + name + '_clst.pk'), csi, 0)

    x = pd.concat([cons, data, voice, features_num, skid_rate, features_cat, chnn_kpi_gb, chnn_kpi_clst_cons,
                   data_clst, voice_clst, cons_cslt], axis=1)

    for i in ['SUM_MINUTES', 'SUM_DATA_MB', 'SUM_DATA_MIN', 'DATA_VOL_MB', 'VOICE_DUR_MIN']:
        for j in ['1', '2', '3', '8', '17', '22', '28', '32', '33', '34']:
            x[i + '#' + j] = x[i] * x['COM_CAT#' + j]
            x[i + '#' + j + 'l'] = np.log(x[i]) * x['COM_CAT#' + j]
            x['l' + i + '#' + j] = x[i] * np.log(x['COM_CAT#' + j])

    for i in range(10):
        x['dSM_VO' + str(i)] = x['SUM_MINUTES_' + str(i)] / x['VOICE_DUR_MIN_' + str(i)]
        x['mSM_VO' + str(i)] = x['SUM_MINUTES_' + str(i)] * x['VOICE_DUR_MIN_' + str(i)]
        x['RATE_' + str(i)] = x['SUM_DATA_MB_' + str(i)] / x['SUM_DATA_MIN_' + str(i)]

    for i in range(10):
        for cl in ['SUM_MINUTES', 'SUM_DATA_MB', 'SUM_DATA_MIN', 'DATA_VOL_MB', 'VOICE_DUR_MIN']:
            for j in ['1', '2', '3', '8', '17', '22', '28', '32', '33', '34']:
                x[cl + '_' + str(i) + '#' + j] = x[cl + '_' + str(i)] * x['COM_CAT#' + j]

    x = x.replace([np.inf, -np.inf], np.nan)
    x = x.fillna(0, axis=0)

    if name == 'train':
        return (x, csi['CSI'])
    else:
        return (x, csi)


def create_ds():
    chnn_kpi = pd.read_pickle('kpi_chnn.pk')
    chnn_kpi_clst = pd.read_pickle('kpi_chnn_clst.pk')

    (X, y) = prepare('train', chnn_kpi, chnn_kpi_clst)
    (x_submit, y_submit) = prepare('test', chnn_kpi, chnn_kpi_clst)

    X.to_pickle('x.pk')
    y.to_pickle('y.pk')
    x_submit.to_pickle('xs.pk')
    y_submit.to_pickle('ys.pk')


def create_prediction():
    prediction = np.array(pd.read_csv('prediction.txt', header=None))
    best = np.array(pd.read_csv('best.txt', header=None))
    csi = pd.read_pickle('train/subs_csi_test.pk')
    prediction_df = pd.DataFrame(prediction)
    best_df = pd.DataFrame(best)
    prediction_df.index = csi.index
    prediction_df.columns = ['pCSI']
    prediction_df.index = csi.index
    best_df.index = csi.index
    best_df.columns = ['bCSI']
    best_df.join(prediction_df).to_pickle('best_prediction.pk')


# prepare and save
create_ds()
# create_prediction()