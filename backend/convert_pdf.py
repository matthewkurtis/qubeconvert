import datetime
import os
import re
import re as regex
from concurrent.futures import process
from decimal import Decimal as dec
from decimal import getcontext
from operator import contains
from pathlib import Path

import fitz
import pandas as pd

getcontext().prec = 3
import time

##### FILE LOCATIONS #####
STATEMENTS_LOCATION = './input_statements'
CSV_OUTPUT = './output_csv/qube_transactions.csv'


##### OBJECT DEFENITIONS #####
class Transaction():
    def __init__(self, date, payee, amount, account_no):
        self.date = date
        self.payee = payee
        self.amount = amount
        self.account_no = account_no

    def as_dict(self):
        return {'date': self.date, 'payee': self.payee, 'amount': self.amount, 'account_no': self.account_no}


##### FUNCTIONS #####
def get_text(filepath: str) -> str:
    ### Open pdf and parse for text
    with fitz.open(filepath) as doc:
        text = ""
        for page in doc:
            text += "\n"
            text += page.get_text().strip()
            print(text)
        return text


def parse_pdf_qube(pdf):
    ### scan the pdf text and separate it into needed data chunks 
    text = (get_text(pdf))
    account_no:str = 'none'

    # Grab the Account Number
    if 'Account Number:' in text:
        account_part_1 = text.split('Account Number: ')[1]
        account_no = account_part_1.split('\n')[0]
        print(f"Account Number {account_no}")
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
    ### Split out unwanted date like page breaks and footers to return clean list of Transaction objects only
    transactions = []
    rows = text.split('\n')
    strip_text = [
        'Page',
        'Date',
        'Description',
        'Amount'
    ]
    stripped_text = [row for row in rows if not any(delete_words in row for delete_words in strip_text)]
    for line in stripped_text:
        if not line:
            pass
        else:
            year = re.match(r'\d\d/\d\d/\d\d\d\d', line)
            if year:
                date_orig = year.group()
                payee = line.split(date_orig)[1]
                date = datetime.datetime.strptime(date_orig, "%m/%d/%Y").strftime("%Y-%m-%d")
            if "$" in line:
                amount = line.replace('$', '')
                transactions.append(Transaction(date, payee, amount, account_no))
    
    return transactions

def print_transaction_overview(transactions):
    # Print out a dataframe and deposit/withdrawal balances for reconciling (helped with checking that there are no missing transactions during development)
    transaction_qty = len(transactions)
    deposits = []
    withdrawals = []
    if transaction_qty != 0:
        for t in transactions:
            amount_no_commas = str(t.amount).replace(",", "")
            amount = round(float(amount_no_commas), 2)
            if amount > 0:
                deposits.append(amount)
            elif amount < 0:
                withdrawals.append(amount)

        # PANDAS DATAFRAME PRINT
        df = pd.DataFrame([x.as_dict() for x in transactions])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        pd.set_option('display.max_rows', None)
        print(df)

        # Reconiciliation Print
        print("\n")
        print(f"----------------- Deposits Total: ${round(sum(deposits), 2)} ({len(deposits)} Deposits)")
        print(f"-------------- Withdrawals Total: ${round(sum(withdrawals), 2)} ({len(withdrawals)} Withdrawal)")
        print(f"-------------------------- Total: ${round((sum(withdrawals) + sum(deposits)), 2)} ({len(withdrawals) + len(deposits)} Items Total) \n")
            
    else:
        # This document is formatted improperly or has no transactions for the period. skip
        print("No transactions found.. skipping document")
        time.sleep(2)


def write_csv(transactions):
    # write to CSV 

    print("WRITING CSV..")
    df = pd.DataFrame([x.as_dict() for x in transactions])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    df.to_csv(CSV_OUTPUT, index=False, header=True)
    print(f"COMPLETE! CHECK FILE IN: {CSV_OUTPUT}")




##### MAIN LOGIC #####
if __name__ == '__main__':
 
    # Get list of Files 
    files = sorted(Path(STATEMENTS_LOCATION).glob('*'))
    if len(files) == 0:
        print(f"\n No files found in directory: {Path(dir)}")
    else:
        # Create a master transaction list
        all_transactions = []
        # For each pdf...
        for file in files:
            if Path(file).suffix == '.pdf':
                print(f"\n >>>>>>>>>> Processing Qube Statement: {file}")
                # Parse The PDF for transactions
                file_transactions = parse_pdf_qube(file)
                # Print some data to reoncile against if necessary
                print_transaction_overview(file_transactions)
                # Write the file's transactions to the master transactions list
                for file_transaction in file_transactions:
                    all_transactions.append(file_transaction)

    # Write the master transactions list out to a csv file
    write_csv(all_transactions)