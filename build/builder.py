import numpy as np
import pandas as pd
from datetime import timedelta
import plotly
import plotly.express as px
from jinja2 import Template, Environment, FileSystemLoader
from build.utils import (
    books, book_color_map, book_color_sequence, color_map,
    dollars, percent, date_display
)


def build(records):
    print('--> computing data from records')

    # records by book
    book_records = {
        b: [x for x in records if x['Book'] == b]
        for b in books
    }

    # deposits, withdraws, profits
    for b in books:
        deposits = 0
        withdraws = 0
        for x in book_records[b]:
            if x['Action'] == 'Deposit':
                deposits += abs(x['Change'])
            if x['Action'] == 'Withdraw':
                withdraws += abs(x['Change'])
            x['Profit'] = x['Balance'] + withdraws - deposits

    # net records
    net_records = []
    current_records = {b: {'Balance': 0, 'Profit': 0} for b in books}
    for x in records:
        current_records[x['Book']] = x
        net_records.append({
            **x,
            'Balance': sum([current_records[b]['Balance'] for b in books]),
            'Profit': sum([current_records[b]['Profit'] for b in books]),
        })

    # date metadata
    last_update = records[-1]['Time']
    last_update_display = date_display(last_update)
    last_update_timestamp = last_update.timestamp()
    min_date = str(records[0]['Time'].date() - pd.Timedelta(1, unit='D'))
    max_date = str(records[-1]['Time'].date() + pd.Timedelta(1, unit='D'))

    # net actions
    net_actions = get_net_actions(records)

    # book values
    book_values, total_value = get_book_values(book_records)

    # betting stats
    betting_stats = get_betting_stats(
        net_records, timespans=[90, 180, 365, 'all'])

    # profit by month
    profit_by_month = get_profit_by_month(net_records)

    # time plotting data
    book_time_series, net_time_series = get_time_series_data(
        book_records, net_records
    )

    # metadata
    meta = {
        'last_update_display': last_update_display,
        'last_update_timestamp': last_update_timestamp,
        'min_date': min_date,
        'max_date': max_date,
        'books': books,
        'book_color_sequence': book_color_sequence,
    }

    print('--> rendering html page')
    jinja_env = Environment(loader=FileSystemLoader(searchpath='templates/'))
    template = jinja_env.get_template('main.html.jinja')
    html = template.render(
        meta=meta,
        net_actions=net_actions,
        book_values=book_values,
        total_value=total_value,
        betting_stats=betting_stats,
        profit_by_month=profit_by_month,
        book_time_series=book_time_series,
        net_time_series=net_time_series,
    )

    outfile = 'index.html'
    with open(outfile, 'w') as f:
        f.write(html)

    print('--> updated %s' % outfile)
    return 0


def get_net_actions(records):
    deposits = [x['Change'] for x in records if x['Action'] == 'Deposit']
    deposits = abs(sum(deposits))
    withdraws = [x['Change'] for x in records if x['Action'] == 'Withdraw']
    withdraws = abs(sum(withdraws))
    wagers = [x['Change'] for x in records if x['Action'] == 'Wager']
    wagers = abs(sum(wagers))
    winnings = [x['Change'] for x in records if x['Action'] == 'Winnings']
    winnings = abs(sum(winnings))

    net_actions = [
        {'type': 'Deposits', 'value': dollars(deposits, comma=True)},
        {'type': 'Withdraws', 'value': dollars(withdraws, comma=True)},
        {'type': 'Wagers', 'value': dollars(wagers, comma=True)},
        {'type': 'Winnings', 'value': dollars(winnings, comma=True)},
    ]
    return net_actions


def get_book_values(book_records):
    book_values = [
        {
            'book': b,
            'value': round(book_records[b][-1]['Profit'], 2),
        }
        for b in books
    ]
    total_value = sum([book_records[b][-1]['Profit'] for b in books])
    total_value = dollars(total_value)
    return book_values, total_value


def get_career_stats(records):
    wagers = [abs(x['Change']) for x in records if x['Action'] == 'Wager']
    career_bets = len(wagers)
    avg_bet_amount = dollars(np.mean(wagers))
    return career_bets, avg_bet_amount


def get_earnings_rate(net_records, timespans=[]):
    earnings_rate = {}
    for span in timespans:
        starting_point = pd.to_datetime(
            net_records[-1]['Time'] - timedelta(days=span)
        )
        subset = [x for x in net_records if x['Time'] >= starting_point]
        profit = subset[-1]['Profit'] - subset[0]['Profit']
        earnings_rate[span] = {
            'timespan': span,
            'per_week': dollars(profit / span * 7),
            'per_day': dollars(profit / span),
            'total': dollars(profit),
        }
    return earnings_rate


def get_betting_stats(net_records, timespans=[]):
    betting_stats = {}
    for span in timespans:
        if span == 'all':
            starting_point = net_records[0]['Time']
            days = (net_records[-1]['Time'] - net_records[0]['Time']).days
        else:
            starting_point = pd.to_datetime(
                net_records[-1]['Time'] - timedelta(days=span)
            )
            days = span
        subset = [x for x in net_records if x['Time'] >= starting_point]
        profit = subset[-1]['Profit'] - subset[0]['Profit']

        wagers = [abs(x['Change']) for x in subset if x['Action'] == 'Wager']
        winnings = [
            abs(x['Change'])
            for x in subset if x['Action'] == 'Winnings' and x['Bonus'] != 'Bonus'
        ]
        bets_placed = len(wagers)
        bets_won = len(winnings)
        win_rate = bets_won / bets_placed
        avg_bet_amount = np.mean(wagers)
        avg_win_amount = np.mean(winnings)

        betting_stats[span] = {
            'timespan': span,
            'profit_per_week': dollars(profit / days * 7),
            'profit_per_day': dollars(profit / days),
            'total_profit': dollars(profit),
            'bets_placed': bets_placed,
            'bets_won': bets_won,
            'win_rate': percent(win_rate),
            'avg_bet_amount': dollars(avg_bet_amount),
            'avg_win_amount': dollars(avg_win_amount),
        }
    return betting_stats


def get_profit_by_month(net_records):
    profit_by_month = []
    periods = pd.date_range(
        net_records[0]['Time'], net_records[-1]['Time'],
        freq='MS'
    )
    for p in periods:
        subset = [
            x for x in net_records
            if x['Time'].year == p.year and x['Time'].month == p.month
        ]
        profit = subset[-1]['Profit'] - subset[0]['Profit']
        profit_by_month.append({
            'month': p.strftime('%b %Y'),
            'profit': round(profit, 0),
            'color': color_map['blue'] if profit >= 0 else color_map['red'],
        })
    return profit_by_month


def get_time_series_data(book_records, net_records):
    book_time_series = [
        {
            'book': b,
            'color': book_color_map[b],
            'timestamp': [int(x['Time'].timestamp()) for x in book_records[b]],
            'time': [str(x['Time']) for x in book_records[b]],
            'time_display': [date_display(x['Time'], year=False) for x in book_records[b]],
            'value': [round(x['Profit'], 2) for x in book_records[b]],
        }
        for b in books
    ]

    net_time_series = {
        'color': color_map['red'],
        'timestamp': [int(x['Time'].timestamp()) for x in net_records],
        'time': [str(x['Time']) for x in net_records],
        'time_display': [date_display(x['Time'], year=False) for x in net_records],
        'value': [round(x['Profit'], 2) for x in net_records],
    }
    return book_time_series, net_time_series
