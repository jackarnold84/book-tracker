import pandas as pd

from read.config import caesars_read_location


def read_caesars():
    print('--> reading caesars')

    data = pd.read_excel(caesars_read_location, sheet_name=None, header=None)
    cells = pd.concat(data.values())[0]

    data = {
        'Time': [],
        'Type': [],
        'Amount': [],
        'Balance': [],
        'Status': []
    }

    i = 0

    while True:

        if not i < len(cells):
            break

        c = cells.iloc[i]

        if '20' in str(c) and str(c).count(':') >= 2 and (' AM ' in str(c) or ' PM ' in str(c)):
            c_dt = str(c).replace('CST', '').replace('EST', '')
            datetime = pd.to_datetime(c_dt)
            data['Time'].append(str(datetime))
        elif c == 'Type':
            data['Type'].append(cells.iloc[i+1])
        elif c == 'Amount':
            data['Amount'].append(cells.iloc[i+1])
        elif c == 'Balance':
            data['Balance'].append(cells.iloc[i+1])
        elif c == 'Status':
            data['Status'].append(cells.iloc[i+1])
            assert len(data['Time']) == len(data['Type']) == \
                len(data['Amount']) == len(data['Balance'])

        i += 1

    df = pd.DataFrame(data)

    df = df.drop_duplicates()
    df = df[df['Status'] == 'Approved']

    df['Book'] = 'Caesars'
    df['Time'] = [x.replace('EDT', '').replace('CDT', '') for x in df['Time']]
    df['Time'] = pd.to_datetime(df['Time'])

    df['Bonus'] = ['Bonus' if x in ['Bonus'] else '' for x in df['Type']]

    action_map = {'Bet': 'Wager', 'Payout': 'Winnings', 'Bonus': 'Winnings', 'Void': 'Winnings',
                  'Deposit': 'Deposit', 'Withdrawal Request': 'Withdraw'}
    df['Action'] = [action_map[x] for x in df['Type']]

    # fix bonus balance sync
    new_balance = list(df['Balance'])
    for i in range(1, df.shape[0]):
        p = df.iloc[i-1]
        r = df.iloc[i]
        if p['Time'] == r['Time'] and abs(p['Amount']) == abs(r['Amount']):
            if p['Bonus'] == 'Bonus':
                new_balance[i] = r['Balance']
                new_balance[i-1] = r['Balance']
            elif r['Bonus'] == 'Bonus':
                new_balance[i] = p['Balance']
                new_balance[i-1] = p['Balance']

    df['New Balance'] = new_balance

    df = df[['Book', 'Time', 'Action', 'Bonus', 'Amount', 'New Balance']]
    df.columns = ['Book', 'Time', 'Action', 'Bonus', 'Change', 'Balance']

    df = df.sort_values('Time')
    df = df.reset_index(drop=True)

    records = df.to_dict(orient='records')
    return records
