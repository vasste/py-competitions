import numpy as np
import pandas as pd
import datetime

def load_consumption(filename):
    return pd.read_csv(filename, delimiter=';', index_col=0, usecols=['SK_ID', 'CELL_LAC_ID'],
                       dtype={'SK_ID': np.int32, 'CELL_LAC_ID': np.int32}, decimal=',')


def load_csi(filename):
    return pd.read_csv(filename, delimiter=';', index_col=0,
                       dtype={'SK_ID': np.int32, 'subs_csi_train': np.int32},
                       converters={
                           'CONTACT_DATE': lambda a: datetime.datetime.strptime("2018." + a, "%Y.%d.%m")},
                       decimal=',')


def load_data(filename):
    return pd.read_csv(filename, delimiter=';', index_col=0,
                       dtype={'SK_ID': np.int32, 'CELL_LAC_ID': np.int32, 'DATA_VOL_MB': np.float64},
                       converters={
                           'START_TIME': lambda a: datetime.datetime.strptime("2018." + a, "%Y.%d.%m %H:%M:%S")},
                       decimal=',')


def load_voice(filename):
    return pd.read_csv(filename, delimiter=';', index_col=0,
                       dtype={'SK_ID': np.int32, 'CELL_LAC_ID': np.int32, 'VOICE_DUR_MIN': np.float64},
                       converters={
                           'START_TIME': lambda a: datetime.datetime.strptime("2018." + a, "%Y.%d.%m %H:%M:%S")},
                       decimal=',')

def load_features(filename):
    cols = {'COM_CAT#1': np.int32, 'SK_ID': np.int32, 'COM_CAT#2': np.int32, 'COM_CAT#3': np.int32, 'BASE_TYPE': object,
     'ACT': object, 'ARPU_GROUP': np.float64, 'COM_CAT#7': np.int32, 'COM_CAT#8': np.float64, 'DEVICE_TYPE_ID': object,
     'INTERNET_TYPE_ID': object, 'REVENUE': np.float64, 'ITC': np.float64, 'VAS': np.float64,
     'RENT_CHANNEL': np.float64,
     'ROAM': np.float64, 'COST': np.float64, 'COM_CAT#17': np.float64, 'COM_CAT#18': np.float64,
     'COM_CAT#19': np.float64, 'COM_CAT#20': np.float64, 'COM_CAT#21': np.float64, 'COM_CAT#22': np.float64,
     'COM_CAT#23': np.float64, 'COM_CAT#25': object, 'COM_CAT#26': object,
     'COM_CAT#27': np.float64, 'COM_CAT#28': np.float64, 'COM_CAT#29': np.float64, 'COM_CAT#30': np.float64,
     'COM_CAT#31': np.float64, 'COM_CAT#32': np.float64, 'COM_CAT#33': np.float64, 'COM_CAT#34': np.float64}
    return pd.read_csv(filename, delimiter=';', index_col=1,
        dtype = cols, decimal=',', usecols=cols.keys())


def convert_pickle():
    # name = 'subs_csi'
    # for t in ['train', 'test']:
    #     load_csi('train/' + name + '_' + t + '.csv').to_pickle('train/' + name + '_' + t + '.pk')
    # name = 'subs_bs_consumption'
    # for t in ['train', 'test']:
    #     load_consumption('train/' + name + '_' + t + '.csv').to_pickle('train/' + name + '_' + t + '_kpi.pk')
    # name = 'subs_bs_data_session'
    # for t in ['train', 'test']:
    #     load_data('train/' + name + '_' + t + '.csv').to_pickle('train/' + name + '_' + t + '.pk')
    # name = 'subs_bs_voice_session'
    # for t in ['train', 'test']:
    #     load_voice('train/' + name + '_' + t + '.csv').to_pickle('train/' + name + '_' + t + '.pk')
    name = 'subs_features'
    for t in ['train', 'test']:
        load_features('train/' + name + '_' + t + '.csv').to_pickle('train/' + name + '_' + t + '.pk')


# convert_pickle()


def load_bs_avg_kpi_column(chunksize):
    dtype_and_index = {'CELL_LAC_ID':np.int32,'CELL_AVAILABILITY_2G':np.float64,'CELL_AVAILABILITY_3G':np.float64,'CELL_AVAILABILITY_4G':np.float64,'CSSR_2G':np.float64,'CSSR_3G':np.float64,'ERAB_PS_BLOCKING_RATE_LTE':np.float64,'ERAB_PS_BLOCKING_RATE_PLMN_LTE':np.float64,'ERAB_PS_DROP_RATE_LTE':np.float64,'HSPDSCH_CODE_UTIL_3G':np.float64,
    'NODEB_CNBAP_LOAD_HARDWARE':np.float64,'PART_CQI_QPSK_LTE':np.float64,'PART_MCS_QPSK_LTE':np.float64,'PROC_LOAD_3G':np.float64,'PSSR_2G':np.float64,'PSSR_3G':np.float64,'PSSR_LTE':np.float64,'RAB_CS_BLOCKING_RATE_3G':np.float64,'RAB_CS_DROP_RATE_3G':np.float64,'RAB_PS_BLOCKING_RATE_3G':np.float64,'RAB_PS_DROP_RATE_3G':np.float64,'RBU_AVAIL_DL':np.float64,
    'RBU_AVAIL_DL_LTE':np.float64,'RBU_AVAIL_UL':np.float64,'RBU_OTHER_DL':np.float64,'RBU_OTHER_UL':np.float64,'RBU_OWN_DL':np.float64,'RBU_OWN_UL':np.float64,'RRC_BLOCKING_RATE_3G':np.float64,'RRC_BLOCKING_RATE_LTE':np.float64,'RTWP_3G':np.float64,'SHO_FACTOR':np.float64,'TBF_DROP_RATE_2G':np.float64,'TCH_DROP_RATE_2G':np.float64,'UTIL_BRD_CPU_3G':np.float64,
    'UTIL_CE_DL_3G':np.float64,'UTIL_CE_HW_DL_3G':np.float64,'UTIL_CE_UL_3G':np.float64,'UTIL_SUBUNITS_3G':np.float64,'UL_VOLUME_LTE':np.float64,'DL_VOLUME_LTE':np.float64,'TOTAL_DL_VOLUME_3G':np.float64,'TOTAL_UL_VOLUME_3G':np.float64}
    reader = pd.read_csv('bs_avg_kpi.csv', delimiter=';', index_col=0, decimal=',', dtype=dtype_and_index,
                             chunksize=chunksize, usecols=dtype_and_index.keys())
    result = None
    for chunk in reader:
        if result is None:
            result = chunk
            continue
        result.append(chunk)

    return result


def load_bs_chnn_kpi_column(chunksize):
    dtype_and_index = {'CELL_LAC_ID':np.int32,'AVEUSERNUMBER':np.float64,'AVEUSERNUMBER_PLMN':np.float64,'AVR_DL_HSPA_USER_3G':np.float64,
    'AVR_DL_R99_USER_3G':np.float64,'AVR_DL_USER_3G':np.float64,'AVR_DL_USER_LTE':np.float64,'AVR_TX_POWER_3G':np.float64,
    'AVR_UL_HSPA_USER':np.float64,'AVR_UL_R99_USER':np.float64,'AVR_UL_USER_3G':np.float64,'AVR_UL_USER_LTE':np.float64,
    'DL_AVR_THROUGHPUT_3G':np.float64,'DL_AVR_THROUGHPUT_LTE':np.float64,'DL_AVR_THROUGHPUT_R99':np.float64,
    'DL_MEAN_USER_THROUGHPUT_LTE':np.float64,'DL_MEAN_USER_THROUGHPUT_DL_2G':np.float64,'DL_MEAN_USER_THROUGHPUT_HSPA3G':np.float64,
    'DL_MEAN_USER_THROUGHPUT_PLTE':np.float64,'DL_MEAN_USER_THROUGHPUT_REL93G':np.float64,'HSDPA_USERS_3G':np.float64,
    'HSUPA_USERS_3G':np.float64,'RBU_USED_DL':np.float64,'RBU_USED_UL':np.float64,'RELATIVE_RBU_USED_DL':np.float64,
    'RELATIVE_RBU_USED_UL':np.float64,'RELATIVE_TX_POWER_3G':np.float64,'UL_AVR_THROUGHPUT_3G':np.float64,
    'UL_AVR_THROUGHPUT_LTE':np.float64,'UL_AVR_THROUGHPUT_R99':np.float64,'UL_MEAN_USER_THROUGHPUT_LTE':np.float64,
    'UL_MEAN_USER_THROUGHPUT_HS3G':np.float64,'UL_MEAN_USER_THROUGHPUT_PLTE':np.float64,'UL_MEAN_USER_THROUGHPUT_REL93G':np.float64}
    reader = pd.read_csv('bs_chnn_kpi.csv', delimiter=';', index_col=0, dtype=dtype_and_index,
                         decimal=',', chunksize=chunksize, usecols=dtype_and_index.keys())
    result = None
    for chunk in reader:
        if result is None:
            result = chunk
            continue
        result.append(chunk)

    return result

# load_bs_avg_kpi_column(1000000).to_pickle('bs_avg_kpi.pk')
# load_bs_chnn_kpi_column(1000000).to_pickle('bs_avg_chnn.pk')
# bs_avg_chnn = pd.read_pickle('bs_avg_chnn' + '.pk')
# bs_avg_chnn = bs_avg_chnn.fillna(0, axis=0)
# bs_avg_chnn = bs_avg_chnn.groupby('CELL_LAC_ID').mean()
# bs_avg_kpi = pd.read_pickle('bs_avg_kpi' + '.pk')
# bs_avg_kpi = bs_avg_kpi.fillna(0, axis=0)
# bs_avg_kpi = bs_avg_kpi.groupby('CELL_LAC_ID').mean()
# zero = bs_avg_chnn.join(bs_avg_kpi, on='CELL_LAC_ID')
# zero = zero.fillna(0, axis=0)
# zero.to_pickle('kpi_chnn' + '.pk')
#
# data = pd.read_pickle('train/subs_bs_data_session_train.pk').groupby('CELL_LAC_ID').mean()
# voice = pd.read_pickle('train/subs_bs_voice_session_train.pk').groupby('CELL_LAC_ID').mean()
# consumption_kpi = pd.read_pickle('train/subs_bs_consumption_train.pk').groupby('CELL_LAC_ID').mean()
#
# kmean_zero = zero.join(consumption_kpi)
# kmean_zero = kmean_zero.join(voice)
# kmean_zero = kmean_zero.join(data)
# kmean_zero = kmean_zero.fillna(0, axis=0)
# kmean_zero.to_pickle('kpi_chnn_kmean' + '.pk')

# cl = pd.read_pickle('kpi_chnn_clst.pk')
# bs_avg_chnn = pd.read_pickle('kpi_chnn' + '.pk')
# bs_avg_chnn_cl = bs_avg_chnn.join(cl)
# bs_avg_chnn = bs_avg_chnn.fillna(0, axis=0)
# bs_avg_chnn[bs_avg_chnn['CELL_CLST']==0].mean()

for name in ['train', 'test']:
    fname = 'subs_bs_consumption_'
    columns = ['SUM_DATA_MB', 'SUM_DATA_MIN', 'SUM_MINUTES']
    date_columns = 'START_TIME'
    data = pd.read_pickle('train/' + fname + name + '.pk')
    chnn_kpi_clst = pd.read_pickle('kpi_chnn_clst.pk')
    dc = data.join(chnn_kpi_clst, on='CELL_LAC_ID')

    clss = 10
    for cl in columns:
        for i in range(clss):
            dc[cl + '_' + str(i)] = dc[cl]
            dc.loc[dc['CELL_CLST'] != i, cl + '_' + str(i)] = 0

    dc = dc.groupby('SK_ID').mean()
    dc = dc.drop(['CELL_LAC_ID', 'CELL_CLST'] + columns, axis=1)
    dc.to_pickle('train/' + fname + name + '_clst.pk')

# voice = pd.read_pickle('train/subs_bs_voice_session_' + name + '.pk')
# dv = data.join(voice)
# cons = pd.read_pickle('train/subs_bs_consumption_' + name + '.pk')
# dvs = dv.join(cons, on='CELL_LAC_ID')
# dvsc = dvs.join(chnn_kpi_clst, on='CELL_LAC_ID')