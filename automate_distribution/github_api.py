import requests
import logging
import argparse
LINK_TO_RETRIEVE = "https://api.github.com/events"
try:
    r = requets.get(LINK_TO_RETRIEVE)
except RequestException as e:
    logging.info(e)

# Retrieve the list of users.

def generate_passwords(user):
    pass


def encrypt_zip_files(zip_file_name):
    pass

def mask_size():
    pass

def create_folder_and_store_files():
    pass




if __name__ == "__main__":
    parser = argparse.ArgumentParse(description="Take in a spreadsheet and select the first column")
    parser.add_argument("spreadsheet_name", help="This is the name of the spreadsheet")
    parser.add_argument("file_size", help="The desired size of the encrypted file")
    parser.add_argument("output_spreadsheet_name", help="Name of the outputted spreadsheet")
    parser.add_argument("output_directory", help="Directory to output file to")
    
    
    
