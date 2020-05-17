import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import gc


def plot_series(time, series, format="-", start=0, end=None):
    global plt
    plt.plot(time[start:end], series[start:end], format)
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.grid(True)


def moving_average_forecast(series, window_size):
    """Forecasts the mean of the last few values.
        If window_size=1, then this is equivalent to naive forecast"""
    forecast = np.array([0.0] * (len(series) + 56))
    for i in range(len(series) - window_size):
        forecast[i + window_size] = series[i:i + window_size].mean()
    return forecast


def is_added_column(cm):
    return 'agg' in cm or 'mean' in cm or 'sum' in cm


def contains_all(items, value):
    for i in items:
        if not (i in value):
            return False
    return True


def aggregate(keys, df):
    summary_key = 'agg_' + '_'.join(keys)
    columns = []
    for cm in df.columns:
        if is_added_column(cm) or "slp" in cm or "lag" in cm:
            continue
        if list(filter(lambda x: x in cm, keys)) == list(keys):
            columns.append(cm)
    # print(columns)
    df[summary_key] = df[columns].sum(axis=1)
    return summary_key


def add_aggregated_columns(source_ds, aggregate_keys):
    columns = []
    for keys in aggregate_keys:
        columns.append(aggregate(keys, source_ds))

    gc.collect()
    return columns


def prepare_ds(calendar_columns, source_ds, lag_columns, agg_columns, rollings, lags):
    ds = source_ds[lag_columns + calendar_columns + agg_columns].copy()
    sma_columns_lags = []
    for i in lags:
        print(i)
        lag_i_columns = ['lag' + str(i) + '_' + cm for cm in lag_columns]
        ds[lag_i_columns] = ds[lag_columns].shift(i)
        sma_columns_lags = sma_columns_lags + lag_i_columns

    ds = ds.dropna()
    sma_columns = lag_columns + agg_columns + sma_columns_lags
    for i in rollings:
        print(i)
        ds[['sma' + str(i) + '_' + cm for cm in sma_columns]] = ds[sma_columns].rolling(window=i).mean()

    ds = ds.dropna()
    gc.collect()
    return ds


def convert_ds_to_learn(df, prices, calendar_columns, target_columns, agg_columns, rollings, lags):
    df_mlt = pd.melt(df, value_vars=target_columns, id_vars=calendar_columns + agg_columns, var_name='id', value_name='target')
    price_mlt = pd.melt(prices[prices.d >= df['d'][0]], value_vars=target_columns, id_vars=['d'], var_name='id', value_name='price')
    df_mlt['price'] = price_mlt['price']

    for cm in agg_columns:
        df_mlt.loc[df_mlt.id.str.contains(cm[-4:]), 'shop'] = df_mlt[df_mlt.id.str.contains(cm[-4:])][cm]
    df_mlt = df_mlt.drop(agg_columns, axis=1)

    for i in lags:
        print(i)
        gc.collect()
        cm = 'lag' + str(i)
        df_mlt_lag = pd.melt(df, value_vars=[cm + '_' + i for i in target_columns], id_vars=['d'], var_name='id',
                             value_name=cm)
        df_mlt[cm] = df_mlt_lag[cm]
        for y in rollings:
            cms_sma = 'sma' + str(y) + '_lag' + str(i)
            df_mlt_lag = pd.melt(df, value_vars=[cms_sma + '_' + i for i in target_columns], id_vars=['d'],
                                 var_name='id', value_name=cms_sma)
            df_mlt[cms_sma] = df_mlt_lag[cms_sma]

    for i in rollings:
        print(i)
        gc.collect()
        cm = 'sma' + str(i)
        sma_agg = [cm + '_' + i for i in agg_columns]
        df_mlt_sma = pd.melt(df, value_vars=[cm + '_' + i for i in target_columns],
                             id_vars=sma_agg, var_name='id', value_name=cm)
        cm_agg = cm + '_shop'
        for cmi in sma_agg:
            df_mlt_sma.loc[df_mlt_sma.id.str.contains(cmi[-4:]), cm_agg] = \
                df_mlt_sma[df_mlt_sma.id.str.contains(cmi[-4:])][cmi]

        df_mlt[cm] = df_mlt_sma[cm]
        df_mlt[cm_agg] = df_mlt_sma[cm_agg]

    return df_mlt.dropna()

