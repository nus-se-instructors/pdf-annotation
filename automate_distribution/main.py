import pandas as pd
import csv
import hashlib
import pyminizip
import os

from Crypto.Cipher import DES
from collections import defaultdict

INPUT_FILE = "./inputs/input.csv"
NAMES = "Names"
TEAMS = "Teams"
PASSWORD = "Password"
ENCODING = "utf-8"


def encrypt_files_in_directory(df):
    # Loop through the output csv file
    # Names, password, hash
    # for each person, encode the jar file in the second column with the jar
    for index, jarfile in enumerate(df[TEAMS]):
        src_filepath = os.path.join("./inputs/input_files/", jarfile + ".jar")
        dst_filepath = os.path.join("./outputs/output_files/", jarfile + ".jar")
        password = df[PASSWORD][index]
        import pdb

        pdb.set_trace()
        pyminizip.compress(src_filepath, None, dst_filepath, password, 0)


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    df[PASSWORD] = df[NAMES].apply(
        lambda x: hashlib.md5(x.encode(ENCODING)).hexdigest()
    )
    df.to_csv("./outputs/output.csv")
    encrypt_files_in_directory(df)
