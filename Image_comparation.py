import csv
import os

import cv2
import numpy as np

import Image_metrics as img_tools


def calc_metrics(orig, processed):
    ish_img = cv2.imread(orig)
    isk_img = cv2.imread(processed)

    mse = np.sum((ish_img - isk_img) ** 2, dtype=np.float64) / (ish_img.shape[0] * ish_img.shape[1])
    # mse = np.square(isk_img - ish_img).mean()
    nmse = np.sum((ish_img - isk_img) ** 2) / np.sum((ish_img ** 2))
    snr = 10 * np.log10(1 / nmse)
    psnr = 10 * np.log10(255 ** 2 / mse)
    print("mse: ", mse, "nmse: ", nmse, "snr: ", snr, "psnr:", psnr)
    return mse, nmse, snr, psnr


def do_comparation(orig_file_list, folders_list):
    PATH = os.path.abspath(os.getcwd())

    res = []
    index = 0

    for folder in folders_list:
        cur_folder_files = img_tools.getListOfNames(PATH + folder, ".bmp")
        for file in cur_folder_files:
            res.append(calc_metrics(orig_file_list[index], file))

        with open(PATH + folder + "\out.csv", "w") as f:
            wr = csv.writer(f)
            wr.writerows(res)
            res = []
        index = index + 1

    return
