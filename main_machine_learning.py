#!/usr/bin/env python3

import argparse
import csv
import os
from functools import partial

from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split

import evaluation
import feature_extractor4
import loader
import preprocessing
from common.qrs_detect import *
from utils import async
from utils import logger
from utils.common import set_seed


def train(data_dir, model_file):
    (X, Y) = loader.load_all_data(data_dir)

    subX = X
    subY = Y

    subX = preprocessing.normalize(subX)
    subY = preprocessing.format_labels(subY)
    print('Input length', len(subX))
    print('Categories mapping', preprocessing.__MAPPING__)

    print("Features extraction started")
    subX = async.apply_async(subX, feature_extractor4.features_for_row)

    np.savez('outputs/processed.npz', x=subX, y=subY)

    # file = np.load('outputs/processed.npz')
    # subX = file['x']
    # subY = file['y']

    print("Features extraction finished")
    subY = subY

    from collections import Counter

    print("Distribution of categories before balancing")
    counter = Counter(subY)
    for key in counter.keys():
        print(key, counter[key])

    Xt, Xv, Yt, Yv = train_test_split(subX, subY, test_size=0.2)

    model = RandomForestClassifier(n_estimators=60, n_jobs=async.get_number_of_jobs())
    model.fit(Xt, Yt)

    joblib.dump(model, model_file)

    Ypredicted = model.predict(Xv)

    evaluation.print_validation_info(Yv, Ypredicted)


def load_model(model_file):
    return joblib.load(model_file)


def classify(record, clf, data_dir):
    x = loader.load_data_from_file(record, data_dir)
    x = normalize_ecg(x)
    x = feature_extractor4.features_for_row(x)

    # as we have one sample at a time to predict, we should resample it into 2d array to classify
    x = np.array(x).reshape(1, -1)

    return preprocessing.get_original_label(clf.predict(x)[0])


def classify_all(data_dir, model_file):
    model = joblib.load(model_file)
    with open(data_dir + '/RECORDS', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')

        func = partial(classify, clf=model, data_dir=data_dir)
        names = [row[0] for row in reader]
        labels = async.apply_async(names, func)

        with open("answers.txt", "a") as f:
            for (name, label) in zip(names, labels):
                f.write(name + "," + label + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ECG classifier")
    parser.add_argument("-r", "--record", default=None, help="record to classify")
    parser.add_argument("-d", "--dir", default="validation", help="dir with validation files")
    parser.add_argument('--train', dest='train', action='store_true')
    parser.set_defaults(train=False)
    args = parser.parse_args()

    logger.enable_logging('ml', args.train)
    set_seed(42)

    model_file = "model.pkl"

    if args.train:
        train(args.dir, model_file)
    elif args.record is not None:
        model = joblib.load(model_file)
        label = classify(args.record, model, args.dir)

        with open("answers.txt", "a") as f:
            f.write(args.record + "," + label + "\n")
    else:
        if os.path.exists("answers.txt"):
            yesno = input("answers.txt already exists, clean it? [y/n]").lower()
            if yesno == "yes" or yesno == "y":
                open('file.txt', 'w').close()
                classify_all(args.dir, model_file)
        else:
            classify_all(args.dir, model_file)
