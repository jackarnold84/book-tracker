books = ['Fanduel', 'Draftkings', 'Caesars']
book_color_map = {
    'Fanduel': '#1F77B4',
    'Draftkings': '#2CA02C',
    'Caesars': '#F2B701'
}
book_color_sequence = ['#1F77B4', '#2CA02C', '#F2B701']
color_map = {
    'blue': '#1F77B4',
    'green': '#2CA02C',
    'yellow': '#F2B701',
    'red': '#D62728',
    'gray': '#7F7F7F',
}


def dollars(x, whole=False, comma=False, plus=False):
    sign = '-' if x < 0 else '+' if plus else ''
    x = abs(x)
    x = round(x) if whole else round(x, 2)
    if whole:
        if comma:
            return f'{sign}${x:,}'
        else:
            return f'{sign}${x}'
    else:
        if comma:
            return f'{sign}${x:,.2f}'
        else:
            return f'{sign}${x:.2f}'


def percent(x):
    return '%.1f%%' % (x * 100)


def date_display(dt, year=True):
    if year:
        return dt.strftime('%b %d, %Y').replace(' 0', ' ')
    else:
        return dt.strftime('%b %d').replace(' 0', ' ')
