import pandas as pd
from read.config import draftkings_read_location


def read_draftkings():
    print('--> reading draftkings')

    data = pd.read_excel(draftkings_read_location, sheet_name=None, header=None)
    cells = pd.concat(data.values())

    data = {
        'Date': [],
        'Time': [],
        'Category': [],
        'Description': [],
        'ID Ref': [],
        'ID': [],
        'Product': [],
        'Change': [],
        'Balance': []
    }

    for i in range(len(cells[0])):
        c = cells[0].iloc[i]

        if i % 9 == 0:
            data['Date'].append(c)
        elif i % 9 == 1:
            data['Time'].append(c)
        elif i % 9 == 2:
            data['Category'].append(c)
        elif i % 9 == 3:
            data['Description'].append(c)
        elif i % 9 == 4:
            data['ID Ref'].append(c)
        elif i % 9 == 5:
            data['ID'].append(c)
        elif i % 9 == 6:
            data['Product'].append(c)
        elif i % 9 == 7:
            data['Change'].append(c)
        elif i % 9 == 8:
            data['Balance'].append(c)

    df = pd.DataFrame(data)
    df = df.drop_duplicates()

    df['Book'] = 'Draftkings'

    df['Datetime'] = [str(df['Date'].iloc[i].date()) +
                      ' ' + df['Time'].iloc[i] for i in range(df.shape[0])]
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    df['Bonus'] = ['Bonus' if x in ['Promotions and Rewards']
                   else '' for x in df['Category']]

    action_map = {'Wagers and Entry Fees and Purchases': 'Wager', 'Winnings': 'Winnings', 'Promotions and Rewards': 'Winnings',
                  'Deposits': 'Deposit', 'Withdraws': 'Withdraw'}
    df['Action'] = [action_map[x] for x in df['Category']]

    df = df[['Book', 'Datetime', 'Action', 'Bonus', 'Change', 'Balance']]
    df.columns = ['Book', 'Time', 'Action', 'Bonus', 'Change', 'Balance']

    df = df.sort_values('Time')
    df = df.reset_index(drop=True)

    records = df.to_dict(orient='records')
    return records
