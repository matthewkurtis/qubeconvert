import datetime
import re
from decimal import Decimal as dec
from decimal import getcontext
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

getcontext().prec = 3
import time

##### FILE LOCATIONS #####
STATEMENTS_LOCATION = './input_statements'
CSV_OUTPUT = './output_csv/qube_transactions.csv'


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
        print(f"Account Number {account_no}")
    else:
        print("No Account Number Found")
        pass

    if 'Transactions' in text:
        # Grab the "Transactions" Chunk
        transactions_part_1 = text.split('Transactions')[1]
        transactions_only = transactions_part_1.split('For questions')[0]
        # print("TRANSACTIONS ONLY:")
        # print(transactions_only)
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
            transactions_list.append(Transaction(date, description, amount, account_no))
    return transactions_list


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

    

def process_pdfs(files):
    # Create a master transaction list
    all_transactions = []
    # For each pdf...
    for file in files:
        if Path(file).suffix == '.pdf':
            print(f"\n >>>>>>>>>> Processing Qube Statement: {file}")
            # Parse The PDF for transactions
            file_transactions = parse_pdf_qube(file)
            # Print some data to reconcile against if necessary
            print_transaction_overview(file_transactions)
            # Write the file's transactions to the master transactions list
            for file_transaction in file_transactions:
                all_transactions.append(file_transaction)
    return all_transactions


def write_csv(transactions):
    # write to CSV 
    print("WRITING CSV..")
    df = pd.DataFrame([x.as_dict() for x in transactions])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    df.to_csv(CSV_OUTPUT, index=False, header=True)
    print(f"COMPLETE! CHECK FILE IN: {CSV_OUTPUT}")


def return_csv(transactions):
    # Return a CSV without writing it to disk
    df = pd.DataFrame([x.as_dict() for x in transactions])
    df.to_csv(index=False, header=True)
    return df


##### MAIN LOGIC TO CALL FOR REMOTE API #####
def csv_to_pdf_web(pdf_files):
    all_transactions = process_pdfs(pdf_files)
    csv = return_csv(all_transactions)
    return csv


##### MAIN LOGIC FOR LOCAL FILES #####
if __name__ == '__main__':
    # Get list of Files 
    local_files = sorted(Path(STATEMENTS_LOCATION).glob('*'))
    if len(local_files) == 0:
        print(f"\n No files found in directory: {Path(dir)}")
    else:
        all_transactions = process_pdfs(local_files)
        write_csv(all_transactions)