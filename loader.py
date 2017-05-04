import csv
from os import path

import scipy.io as sio
import preprocessing

# Default dir where data set is stored
__DATA_DIR = '/usr/share/ml_data_sets/CinC_ECG/training2017'
FREQUENCY = 300


def load_all_data(data_path=__DATA_DIR, shuffle=True):
    """
    Loads all the dataset
    :param data_path: directory where the dataset is located
    :param shuffle: whether to shuffle loaded data
    :return: tuple of (array of row records, array of labels)
    """
    (data, labels) = __load_data(data_path)
    if shuffle:
        return preprocessing.shuffle_data(data, labels)
    return data, labels


def check_has_example(example_name, data_path=__DATA_DIR):
    file_path = data_path + '/' + example_name + '.mat'
    return path.exists(file_path) and path.isfile(file_path)


def load_data_from_file(example_name, data_path=__DATA_DIR):
    """
    Loads data from MatLab file for given example
    :return: features for given example
    """
    test = sio.loadmat(data_path + '/' + example_name + '.mat')
    content = test['val'][0]
    return content


def __load_data(data_path=__DATA_DIR):
    data = []
    labels = []
    with open(data_path + '/REFERENCE.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            file_name = row[0]
            label = row[1]
            data.append(load_data_from_file(file_name, data_path))
            labels.append(label)

    return (data, labels)
