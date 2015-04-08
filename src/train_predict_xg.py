#!/usr/bin/env python

from __future__ import division
from sklearn.cross_validation import StratifiedKFold
from sklearn.datasets import load_svmlight_file
from sklearn.metrics import log_loss

import argparse
import logging
import numpy as np
import time

import xgboost as xgb


logging.basicConfig(format='%(asctime)s   %(levelname)s   %(message)s',
                    level=logging.DEBUG)


def train_predict(train_file, test_file, predict_valid_file, predict_test_file,
                  n_est=100, depth=4, lrate=.1, n_fold=5):

    logging.info('Loading training and test data...')
    X, y = load_svmlight_file(train_file)
    X_tst, _ = load_svmlight_file(test_file)

    clf = xgb.XGBClassifier(max_depth=depth, learning_rate=lrate,
                            n_estimators=n_est)
    """
    X, y_valtrn = load_svmlight_file(valid_train_file)
    X_valtst, y_valtst = load_svmlight_file(valid_test_file)

    logging.info('Validation...')
    clf.fit(X_valtrn, y_valtrn)
    p_valtst = clf.predict_proba(X_valtst)[:, 1]
    lloss = log_loss(y_valtst, p_valtst)

    logging.info('Log Loss = {:.4f}'.format(lloss))
    """

    cv = StratifiedKFold(y, n_folds=n_fold, shuffle=True, random_state=2015)

    logging.info('Cross validation...')
    p_val = np.zeros_like(y)
    lloss = 0.
    for i_trn, i_val in cv:
        clf.fit(X, y)
        p_val[i_val] = clf.predict_proba(X[i_val])[:, 1]
        lloss += log_loss(y[i_val], p_val[i_val])

    logging.info('Log Loss = {:.4f}'.format(lloss / n_fold))

    logging.info('Retraining with 100% data...')
    clf.fit(X, y)
    p_tst = clf.predict_proba(X_tst)[:, 1]

    logging.info('Saving predictions...')
    np.savetxt(predict_valid_file, p_val, fmt='%.6f')
    np.savetxt(predict_test_file, p_tst, fmt='%.6f')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-file', required=True, dest='train_file')
    parser.add_argument('--test-file', required=True, dest='test_file')
    parser.add_argument('--predict-valid-file', required=True,
                        dest='predict_valid_file')
    parser.add_argument('--predict-test-file', required=True,
                        dest='predict_test_file')
    parser.add_argument('--n-est', type=int, dest='n_est')
    parser.add_argument('--depth', type=int, dest='depth')
    parser.add_argument('--lrate', type=float, dest='lrate')

    args = parser.parse_args()

    start = time.time()
    train_predict(train_file=args.train_file,
                  test_file=args.test_file,
                  predict_valid_file=args.predict_valid_file,
                  predict_test_file=args.predict_test_file,
                  n_est=args.n_est,
                  depth=args.depth,
                  lrate=args.lrate)
    logging.info('finished ({:.2f} min elasped)'.format((time.time() - start) /
                                                        60))
