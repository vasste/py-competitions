import pandas as pd
import numpy as np
from skopt import BayesSearchCV
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier
from telecom.train_columns import *

# include below until https://github.com/scikit-optimize/scikit-optimize/issues/718 is resolved
class BayesSearchCV(BayesSearchCV):
    def _run_search(self, x): raise BaseException('Use newer skopt')

ITERATIONS = 10 # 1000
TRAINING_SIZE = 100000 # 20000000
TEST_SIZE = 25000
np.random.seed(83)


X = pd.read_pickle('x.pk')[train_columns]
y = pd.read_pickle('y.pk')
bayes_cv_tuner = BayesSearchCV(
    estimator = XGBClassifier(
        n_jobs=4,
        objective='binary:logistic',
        eval_metric='auc',
        silent=1,
        tree_method='approx'
    ),
    search_spaces={
        'learning_rate': (0.01, 1.0, 'log-uniform'),
        'min_child_weight': (0, 10),
        'max_depth': (0, 50),
        'max_delta_step': (0, 20),
        'subsample': (0.01, 1.0, 'uniform'),
        'colsample_bytree': (0.01, 1.0, 'uniform'),
        'colsample_bylevel': (0.01, 1.0, 'uniform'),
        'reg_lambda': (1e-9, 1000, 'log-uniform'),
        'reg_alpha': (1e-9, 1.0, 'log-uniform'),
        'gamma': (1e-9, 0.5, 'log-uniform'),
        'min_child_weight': (0, 5),
        'n_estimators': (50, 100),
        'scale_pos_weight': (1e-6, 500, 'log-uniform')
    },
    scoring='roc_auc',
    cv=StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=83
    ),
    n_jobs=4,
    n_iter=ITERATIONS,
    verbose=0,
    refit=True,
    random_state=83
)


def status_print(optim_result):
    """Status callback durring bayesian hyperparameter search"""

    # Get all the models tested so far in DataFrame format
    all_models = pd.DataFrame(bayes_cv_tuner.cv_results_)

    # Get current parameters and the best parameters
    best_params = pd.Series(bayes_cv_tuner.best_params_)
    print('Model #{}\nBest ROC-AUC: {}\nBest params: {}\n'.format(
        len(all_models),
        np.round(bayes_cv_tuner.best_score_, 4),
        bayes_cv_tuner.best_params_
    ))

    # Save all model results
    clf_name = bayes_cv_tuner.estimator.__class__.__name__
    all_models.to_csv(clf_name + "_cv_results.csv")


result = bayes_cv_tuner.fit(X.values, y.values, callback=status_print)
