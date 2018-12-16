import numpy as np
import pandas as pd
from sklearn import ensemble
from sklearn.linear_model import LogisticRegressionCV, LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from xgboost import XGBClassifier

from telecom.train_columns import *


def run_seed(random, est=0):
    X = pd.read_pickle('x.pk')[train_columns]
    y = pd.read_pickle('y.pk')
    return run_seed_xy(X, y, random, est)


def run_seed_xy(X, y, random, est=0):
    np.random.seed(random)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=random)

    clf = create_classifier(random, est)
    classify(X_train, y_train, clf)
    y_train_predict = clf.predict(X_train)
    y_test_predict = clf.predict(X_test)
    y_test_score = clf.predict_proba(X_test)
    y_train_score = clf.predict_proba(X_train)
    roc_train = roc_auc_score(y_train, y_train_score[:, 1])
    roc_test = roc_auc_score(y_test, y_test_score[:, 1])
    print(roc_test, roc_train, random)
    print(np.mean(y_train != y_train_predict))
    print(np.mean(y_test != y_test_predict))

    if roc_test > 0.55:
        x_submit = pd.read_pickle('xs.pk')
        x_submit = x_submit[train_columns]
        y_submit = pd.read_pickle('ys.pk')
        x_submit = x_submit.reindex(y_submit.index)
        y_submit_predict = clf.predict_proba(x_submit)
        current_best = np.array(pd.read_csv('best.txt', header=None))
        print(np.mean(current_best - y_submit_predict[:, 1]))
        with open('prediction.txt', 'w') as f:
            for clazz in y_submit_predict:
                f.write(str(clazz[1]) + "\n")

    # importances = clf.feature_importances_
    # indices = np.argsort(importances)[::-1]
    # feature_names = X.columns
    # print("Feature importance:")
    # for f, idx in enumerate(indices):
    #     # if importances[idx] > .001:
    #     print("{:2d}. feature '{:5s}' ({:.4f})".format(f + 1, feature_names[idx], importances[idx]))

    return roc_test, roc_train


def find_seed():
    X = pd.read_pickle('x.pk')[train_columns]
    y = pd.read_pickle('y.pk')
    X = X.reindex(y.index)
    for i in range(1000):
        print(i + 83)
        cross_validation_xy(X, y, i + 83)


def cross_validation_xy(X, y, seed):
    kf = StratifiedKFold(random_state=seed, n_splits=10, shuffle=True)
    clf = create_classifier(seed)
    scores = cross_val_score(clf, X, y, cv=kf, scoring='roc_auc')
    print("CV scores:", scores)
    print("mean:", np.mean(scores))
    print("median:", np.median(scores))
    print("min:", np.min(scores))
    print("std:", np.std(scores))


def cross_validation(seed):
    X = pd.read_pickle('x.pk')[train_columns]
    y = pd.read_pickle('y.pk')
    cross_validation_xy(X, y, seed)


def tune(seed):
    np.random.seed(seed)
    X = pd.read_pickle('x.pk')
    y = pd.read_pickle('y.pk')

    X = X[train_columns]
    X = X.reindex(y.index)

    xgb_model = create_classifier(seed)
    parameters = {'min_child_weight': np.arange(0.1, 10.1, 0.1)}
    kf = StratifiedKFold(random_state=seed, n_splits=5, shuffle=True)
    clf = GridSearchCV(xgb_model, parameters, n_jobs=4, cv=kf, scoring='roc_auc', verbose=2, refit=True)

    xtr, xvl, ytr, yvl = train_test_split(X, y, test_size=0.3, random_state=seed)
    classify(xtr, ytr, clf)
    best_parameters, score, _ = max(clf.cv_results_, key=lambda x: x[1])
    print('Raw AUC score:', score)
    for param_name in sorted(best_parameters.keys()):
        print("%s: %r" % (param_name, best_parameters[param_name]))

    x_submit = pd.read_pickle('xs.pk')
    x_submit = x_submit[train_columns]
    y_submit = pd.read_pickle('ys.pk')
    x_submit = x_submit.reindex(y_submit.index)
    y_submit_predict = clf.predict_proba(x_submit)
    current_best = np.array(pd.read_csv('best.txt', header=None))
    print(np.mean(current_best - y_submit_predict[:, 1]))
    with open('prediction.txt', 'w') as f:
        for clazz in y_submit_predict:
            f.write(str(clazz[1]) + "\n")


def test(seed):
    np.random.seed(seed)
    X = pd.read_pickle('x.pk')[train_columns]
    y = pd.read_pickle('y.pk')
    X = X.reindex(y.index)
    clf = create_classifier(seed)
    classify(X, y, clf)

    x_submit = pd.read_pickle('xs.pk')
    x_submit = x_submit[train_columns]
    y_submit = pd.read_pickle('ys.pk')
    x_submit = x_submit.reindex(y_submit.index)
    y_submit_predict = clf.predict_proba(x_submit)
    current_best = np.array(pd.read_csv('best.txt', header=None))
    print(np.mean(current_best - y_submit_predict[:, 1]))
    with open('prediction_test.txt', 'w') as f:
        for clazz in y_submit_predict:
            f.write(str(clazz[1]) + "\n")
    # importances = clf.feature_importances_
    # indices = np.argsort(importances)[::-1]
    # feature_names = X.columns
    # print("Feature importance:")
    # for f, idx in enumerate(indices):
    #     # if importances[idx] > .001:
    #     print("{:2d}. feature '{:5s}' ({:.4f})".format(f + 1, feature_names[idx], importances[idx]))


def classify(X, y, classifier):
    # classifier.fit(X, y, eval_metric='auc')
    classifier.fit(X, y)


def create_classifier(seed, est=0):
    # fit = LogisticRegression(random_state=seed, solver='newton-cg', n_jobs=4, max_iter=1000, class_weight={0:.7, 1:.9}, C=10)
    fit = LogisticRegressionCV(random_state=seed, solver='newton-cg', max_iter=1000, n_jobs=4, cv=5, scoring='roc_auc')
    # fit = ensemble.GradientBoostingClassifier(n_estimators=50, random_state=seed, min_samples_leaf=0.15, max_depth=3, learning_rate=0.1)
    # fit = XGBClassifier(random_state=seed, n_jobs=4, n_estimators=50, learning_rate=0.1, max_depth=3)
    # fit = ensemble.RandomForestClassifier(n_estimators=50, random_state=seed, n_jobs=4, max_depth=2)

    # fit.set_params(**{'colsample_bylevel': 0.8907837883211248, 'colsample_bytree': 0.9100348740381765, 'gamma': 0.024073152296932174,
    #  'learning_rate': 0.05147525285909681, 'max_delta_step': 1, 'max_depth': 33, 'min_child_weight': 4,
    #  'n_estimators': 88, 'reg_alpha': 0.11926067214113158, 'reg_lambda': 23.39463535076406,
    #  'scale_pos_weight': 0.9261765032432218, 'subsample': 0.8440035524838023})

    return fit


# play with model
# 83 87 88
seed = 83
# tune(83)
# cross_validation(seed)
run_seed(seed)
test(seed)
# find_seed()
# max_depths = range(1,6,2)
# train_results = []
# test_results = []
# for eta in max_depths:
#     tt, tn = run_seed(83, eta)
#     test_results.append(tt)
#     train_results.append(tn)
#
# line1, = plt.plot(max_depths, train_results, 'b', label='Train AUC')
# line2, = plt.plot(max_depths, test_results, 'r', label='Test AUC')
#
# plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
#
# plt.ylabel('AUC score')
# plt.xlabel('learning rate')
# plt.show()
