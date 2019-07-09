import pandas as pd
import csv
import hashlib

from Crypto.Cipher import DES
from collections import defaultdict
from os import listdir

INPUT_FILE = "./inputs/input.csv"


def encrypt_files_in_directory():

    pass

    # Encrypt each file with a password


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    df["Password"] = df["Names"].apply(
        lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()
    )
    df.to_csv("./outputs/output.csv")
