import datetime
import re
from decimal import Decimal as dec
from decimal import getcontext
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

getcontext().prec = 3
import time


##### OBJECT DEFENITIONS #####
class Transaction():
    def __init__(self, date, description, amount, account_no):
        self.date = date
        self.description = description
        self.amount = amount
        self.account_no = account_no

    def as_dict(self):
        return {'date': self.date, 'description': self.description, 'amount': self.amount, 'account_no': self.account_no}


##### FUNCTIONS #####
def get_text(filepath: str) -> str:
    doc = PdfReader(filepath)
    text = ""
    for page in doc.pages:
        text += page.extract_text().strip() + '\n'
    return text

def parse_pdf_qube(pdf):
    ### scan the pdf text and separate it into needed data chunks 
    text = (get_text(pdf))
    account_no:str = 'none'

    # Grab the Account Number
    if 'Account Number:' in text:
        account_part_1 = text.split('Account Number:')[1].strip()
        account_no = account_part_1.split('\n')[0]
    else:
        print("No Account Number Found")
        pass

    if 'Transactions' in text:
        # Grab the "Transactions" Chunk
        transactions_part_1 = text.split('Transactions')[1]
        transactions_only = transactions_part_1.split('For questions')[0]
        return clean_transactions(transactions_only, account_no)
    else:
        print("No Transactions Segment found in PDF")
        # TODO: Throw error


def clean_transactions(text, account_no):
    transactions_list = []
    ### Split out unwanted date like page breaks and footers to return clean list of Transaction objects only
    text = text.replace('\n', ' ').replace('\r', ' ')
    trans_pattern = r'\d{2}/\d{2}/\d{4}.*?-?\$[\d,]+\.\d{2}'
    transactions = re.findall(trans_pattern, text)
    for transaction in transactions:

        # Define the regex pattern
        pattern = r'^(\d{2}/\d{2}/\d{4})\s*(.*?)\s*(-?\$[\d,]+\.\d{2})$'

        # Use the re.search() function to find the pattern in the string
        match = re.search(pattern, transaction)

        # Extract the groups if a match is found
        if match:
            groups = match.groups()
            # date = groups[0]
            date = datetime.datetime.strptime(groups[0], "%m/%d/%Y").strftime("%Y-%m-%d")
            description = groups[1]
            amount = groups[2]
            # Remove commas and dollar signs from the amount string, if present
            amount = amount.replace(',', '').replace('$', '')
            # Add to the list as a Transaction object
            transactions_list.append(Transaction(date=date, description=description, amount=amount, account_no=account_no))
    return transactions_list

    

def process_pdfs(files):
    # Create a master transaction list
    all_transactions = []
    # For each pdf...
    for file in files:
        # Parse The PDF for transactions
        file_transactions = parse_pdf_qube(file)
        # Write the file's transactions to the master transactions list
        for file_transaction in file_transactions:
            all_transactions.append(file_transaction)
    return all_transactions


def return_csv(transactions):
    # Return a CSV without writing it to disk
    df = pd.DataFrame([x.as_dict() for x in transactions])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    csv = df.to_csv(index=False, header=True)
    return csv


##### MAIN LOGIC TO CALL FOR REMOTE API #####
def csv_to_pdf_web(pdf_files):
    return return_csv(process_pdfs(pdf_files))