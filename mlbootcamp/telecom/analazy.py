import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

Xy = pd.read_pickle('bs_avg_kpi_sk.pk')
y = Xy['CSI']
for cl in Xy.columns:
    cl_std = Xy.std()[cl]
    if not (math.isnan(cl_std) or cl_std == 0):
        Xy[cl] = (Xy[cl] - Xy.mean()[cl]) / cl_std
Xy['CSI'] = y

for i in Xy.columns:
    print(i)
    for cl in Xy.columns:
        if i > cl:
            plt.scatter(Xy[cl][Xy['CSI'] == 1],
                        Xy[i][Xy['CSI'] == 1],
                        alpha=0.75,
                        color='red',
                        label='+')

            plt.scatter(Xy[cl][Xy['CSI'] == 0],
                        Xy[i][Xy['CSI'] == 0],
                        alpha=0.75,
                        color='blue',
                        label='-')

            plt.xlabel(cl)
            plt.ylabel(i)
            plt.legend(loc='best')
            plt.show()
