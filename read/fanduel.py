import pandas as pd
from read.config import fanduel_read_location


def read_fanduel():
    print('--> reading fanduel')

    data = pd.read_excel(fanduel_read_location, sheet_name=None, header=None)
    df = pd.concat(data.values())
    df.columns = ['PRODUCT', 'TRANSACTION ID', 'DATE', 'TYPE',
                  'DETAILS', 'SOURCE', 'CHANGE', 'BEFORE', 'BALANCE']
    df = df[['PBT' not in str(x) for x in df['CHANGE']]]
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)

    df['DATE'] = [x.replace('ET', '') for x in df['DATE']]
    df['DATE'] = pd.to_datetime(df['DATE'])

    df = df[df['TYPE'].isin(
        ['Wager', 'Winnings', 'Bonus', 'Manual Adjustment', 'Deposit', 'Withdraw'])]

    df = pd.DataFrame(df)
    df['BONUS'] = list(df['TYPE'])
    df['BOOK'] = 'Fanduel'

    df = df.sort_values('TRANSACTION ID', ascending=False)

    df = df[['BOOK', 'DATE', 'TYPE', 'BONUS', 'CHANGE', 'BALANCE']]
    df.columns = ['Book', 'Time', 'Action', 'Bonus', 'Change', 'Balance']

    df['Bonus'] = ['Bonus' if x in ['Bonus', 'Manual Adjustment']
                   else '' for x in df['Bonus']]

    action_map = {'Wager': 'Wager', 'Winnings': 'Winnings', 'Bonus': 'Winnings', 'Manual Adjustment': 'Winnings',
                  'Deposit': 'Deposit', 'Withdraw': 'Withdraw'}
    df['Action'] = [action_map[x] for x in df['Action']]

    df = df.sort_values('Time')
    df = df.reset_index(drop=True)

    # fix balance errors
    for i in range(1, df.shape[0]):
        r_prev = df.iloc[i-1]
        r_curr = df.iloc[i]

        if (abs(r_curr['Change']) <= 150) and (r_prev['Balance'] - r_curr['Balance'] > 150):
            df.iloc[i, 5] = r_prev['Balance'] + r_curr['Change']

    records = df.to_dict(orient='records')
    return records
