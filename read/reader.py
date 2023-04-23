import pandas as pd
from read.fanduel import read_fanduel
from read.draftkings import read_draftkings
from read.caesars import read_caesars
from read.config import book_list, processed_data_file


def get():
    print('--> reading %s' % processed_data_file)
    df = pd.read_csv(processed_data_file)
    df['Time'] = pd.to_datetime(df['Time'])
    records = df.to_dict(orient='records')
    return records


def read(books=[]):
    books = books or book_list  # update all by default
    
    records_to_add = []
    if 'fanduel' in books:
        records_to_add.append(read_fanduel())
    if 'draftkings' in books:
        records_to_add.append(read_draftkings())
    if 'caesars' in books:
        records_to_add.append(read_caesars())

    records = [r for arr in records_to_add for r in arr]
    print('--> adding %d new records' % len(records))
    update_data(records)


def update_data(new_records):

    def get_record_key(x):
        balance = x.get('Balance')
        return (
            x['Book'],
            int(x['Time'].to_julian_date() * 10000),
            x['Action'],
            int(balance * 100),
        )

    current_df = pd.read_csv('processed_data/transactions.csv')
    current_df['Time'] = pd.to_datetime(current_df['Time'])
    records = current_df.to_dict(orient='records')

    data_dict = {}
    for r in records:
        data_dict[get_record_key(r)] = r
    
    for r in new_records:
        data_dict[get_record_key(r)] = r
    
    new_df = pd.DataFrame(data_dict.values())
    new_df = new_df.sort_values(['Time', 'Book', 'Balance', 'Action'])
    new_df.to_csv(processed_data_file, index=False)
    print('--> updated %s' % processed_data_file)
