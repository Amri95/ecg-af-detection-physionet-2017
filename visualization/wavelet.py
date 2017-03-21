import random

import math
import numpy as np
import matplotlib.pyplot as plt
from pywt import dwt, wavedec
from scipy.stats import stats

from qrs_detect import r_detect

plt.rcParams["figure.figsize"] = (20, 6)

seed = 42
random.seed(seed)
np.random.seed(seed)
print("Seed =", seed)

import loader
import preprocessing
import feature_extractor

from qrs_detect2 import *

(X, Y) = loader.load_all_data()
(Y, mapping) = preprocessing.format_labels(Y)
print('Input length', len(X))
print('Categories mapping', mapping)


def trimboth(row, portion):
    filter = portion * max(
        math.fabs(np.amin(row)),
        abs(np.amax(row))
    )

    return np.array([x if -filter < x < filter else 0 for x in row ])


def plot_wavelet(row, clazz):
    a, d1, d2 = wavedec(row, 'db1', level=2)

    print(clazz)
    print('Mean', np.mean(d1))
    print('Std', np.std(d1))
    print('Mean', np.mean(d2))
    print('Std', np.std(d2))

    plt.subplot(4, 1, 1)
    plt.plot(range(len(row)), row, 'g-')
    plt.ylabel("ECG:" + clazz)

    plt.subplot(4, 1, 2)
    plt.plot(range(len(a)), a, 'g-')
    plt.ylabel("Wavelet")

    d1 = trimboth(d1, 0.1)
    d2 = trimboth(d2, 0.1)

    plt.subplot(4, 1, 3)
    plt.plot(range(len(d1)), d1, 'g-')
    plt.ylabel("D1")

    plt.subplot(4, 1, 4)
    plt.plot(range(len(d2)), d2, 'g-')
    plt.ylabel("D2")

    print('Mean', np.mean(d1))
    print('Std', np.std(d1))
    print('Mean', np.mean(d2))
    print('Std', np.std(d2))

    plt.show()


# Normal: A00001, A00002, A0003, A00006
plot_wavelet(loader.load_data_from_file("A00001"), "Normal")
# AF: A00004, A00009, A00015, A00027
plot_wavelet(loader.load_data_from_file("A00004"), "AF rhythm")
plot_wavelet(loader.load_data_from_file("A00009"), "AF rhythm")
plot_wavelet(loader.load_data_from_file("A00015"), "AF rhythm")
plot_wavelet(loader.load_data_from_file("A00027"), "AF rhythm")
# Other: A00005, A00008, A00013, A00017
plot_wavelet(loader.load_data_from_file("A00005"), "Other rhythm")
plot_wavelet(loader.load_data_from_file("A00008"), "Other rhythm")
plot_wavelet(loader.load_data_from_file("A00013"), "Other rhythm")
plot_wavelet(loader.load_data_from_file("A00017"), "Other rhythm")
# Noisy: A00205, A00585, A01006, A01070
plot_wavelet(loader.load_data_from_file("A00205"), "Noisy signal")
plot_wavelet(loader.load_data_from_file("A00585"), "Noisy signal")
plot_wavelet(loader.load_data_from_file("A01006"), "Noisy signal")
plot_wavelet(loader.load_data_from_file("A01070"), "Noisy signal")
