import pandas as pd
import csv
import hashlib
from Crypto.Cipher import DES
from collections import defaultdict


INPUT_FILE = "./inputs/input.csv"


def encrypt_file():
    pass


def generate_password_list(student_names):
    """
    Takes in a series of student names and returns a list of dictionaries
    """
    password_list = []
    for name in student_names:
        password_list.append(
            {"Name": name, "Password": hashlib.md5(name.encode("utf-8")).hexdigest()}
        )
    return password_list


def write_dict_to_csv(password_list):
    """
    Write dictionary to output csv file
    """
    csv_columns = ["Name", "Password"]
    csv_file = "./outputs/output.csv"
    try:
        with open(csv_file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for item in password_list:
                writer.writerow(item)
    except IOError:
        print("I/O error")
        return False
    return True


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    names = df["Names"]
    password_list = generate_password_list(names)
    if write_dict_to_csv(password_list):
        print("Success")
    else:
        print("Please Check your csv file")
    # print(teams)
