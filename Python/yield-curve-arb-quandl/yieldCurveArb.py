import quandl
import datetime
import requests
from bs4 import BeautifulSoup
from pylab import arange, xlabel, ylabel, title, plot, show, legend
import statistics

# Treasury Reference: https://www.treasurydirect.gov/webapis/webapisecurities.htm
# Quandl Reference: https://docs.quandl.com/docs/parameters-2

# Assign the Quandl API key
quandl.ApiConfig.api_key = '<fill me in>'

# Set up initial header info and URL for Treasury bond prices
treasury_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                                  'Chromium/55.0.2883.87 Chrome/55.0.2883.87 Safari/537.36', 'Accept': 'text/html',
                    'Referer': 'https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate.htm',
                    'Origin': 'https://www.treasurydirect.gov', 'Host': 'www.treasurydirect.gov'}

treasury_prices = 'https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate.htm'

def convertDate(dt):

    return str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day)

def getYields(start_date, end_date):

    # Convert start date and end date into Quandl formatting
    start_month = convertDate(start_date)
    end_month = convertDate(end_date)

    # Request US Treasury Yields per https://www.quandl.com/data/USTREASURY/YIELD
    rates = quandl.get('USTREASURY/YIELD', start_date=start_month, end_date=end_month, collapse='monthly')

    return rates

def parseReturn(prices_html):

    # Parse the html and extract the relevant table info
    prices_soup = BeautifulSoup(prices_html.content, 'lxml')
    return prices_soup.find(class_='data1')

def retrieveBondInfo(t_stamp):

    # Initialize the request session to to account for header persistence
    s = requests.Session()

    # Make initial request for treasury securities
    prices_html = s.post(treasury_prices,
                         data={'priceDate.month': t_stamp.month, 'priceDate.day': t_stamp.day,
                               'priceDate.year': t_stamp.year, 'submit': 'Show Prices'},
                         headers=treasury_headers)

    table = parseReturn(prices_html)

    # In the event the date is a weekend
    # Request prices that are a day before, and keep moving back
    # until you find a day with prices
    temp_day = t_stamp.day
    while table is None:

        temp_day = temp_day - 1

        prices_html = s.post(treasury_prices,
                             data={'priceDate.month': t_stamp.month, 'priceDate.day': temp_day,
                                   'priceDate.year': t_stamp.year, 'submit': 'Show Prices'},
                             headers=treasury_headers)

        table = parseReturn(prices_html)

    return table

def assignFirstBond(td_arr):

    return True, [td_arr[0].text, td_arr[1].text, td_arr[2].text, td_arr[3].text, td_arr[6].text]

def updateCurrentPrice(td_arr, current_position, yields):

    if td_arr[0].text == current_position['2 YR'][0]:

        # Add current price if not there
        if len(current_position['2 YR']) == 5:
            current_position['2 YR'].append(td_arr[6].text)
            current_position['2 YR'].append(yields['2 YR'])

        # Update current price if already there
        else:
            current_position['2 YR'][5] = td_arr[6].text

    else:

        # Add current price if not there
        if len(current_position['10 YR']) == 5:
            current_position['10 YR'].append(td_arr[6].text)
            current_position['10 YR'].append(yields['10 YR'])

        # Update current price if already there
        else:
            current_position['10 YR'][5] = td_arr[6].text

def calcLongShort(yield_dict):

    # Comparing (10 YR yield - 2 YR yield) of historical vs current
    hist_diff = yield_dict['hist'][1] - yield_dict['hist'][0]
    current_diff = yield_dict['current'][1] - yield_dict['current'][0]

    # Momentum strategy based on previous period vs this period yield difference
    # If converging, take converging position
    # If diverging, take diverging position
    if hist_diff > current_diff:
        return 'short'
    else:
        return 'long'

def calcDollarDuration(par, coupon, ytm, num_payments):

    # Convert coupon and ytm into appropriate per-payment values
    coupon_payment = coupon * .5
    ytm_rate = (ytm / 200)

    # Break down dP/dY into two components
    first_term = (coupon_payment / (ytm_rate ** 2)) * (1 - (1 / ((1 + ytm_rate) ** num_payments)))
    second_term = (num_payments * (par - (coupon_payment / ytm_rate)) / ((1 + ytm_rate) ** (num_payments + 1)))

    return first_term + second_term


def calcWeights(current_position):

    # current_position:
        # [0]=cusip, [1]=type, [2]=coupon, [3]=maturity, [4]=purchase price, [5]=current price, [6]=yield
        # ['2 YR'] = 2-year bond & ['10 YR'] = 10-year bond

    # Calcluate dollar duration ($duration)
    # Because we only hold for 3 months on average, we never receive a coupon payment
    two_dd = calcDollarDuration(100, float(str(current_position['2 YR'][2]).replace('%', '')),
                                float(current_position['2 YR'][6]), 2 * 2)
    ten_dd = calcDollarDuration(100, float(str(current_position['10 YR'][2]).replace('%', '')),
                                float(current_position['10 YR'][6]), 10 * 2)

    # Assuming a weight of 100 for the purchase of 10-years, calculate weight of 2-year
    ten_weight = 1
    two_weight = int(ten_weight * (ten_dd / two_dd))

    return two_weight, ten_weight

def calcPNL(current_position,):

    # Get Long / Short positions
    two_ls = calcLongShort(yield_dict)

    # Weights for bond1 and bond2
    two_weight, ten_weight = calcWeights(current_position)

    # Calculate 2-year and 10-year profit / loss
    if two_ls == 'long':
        two_price_diff = float(current_position['2 YR'][5]) - float(current_position['2 YR'][4])
        ten_price_diff = float(current_position['10 YR'][4]) - float(current_position['10 YR'][5])
    else:
        two_price_diff = float(current_position['2 YR'][4]) - float(current_position['2 YR'][5])
        ten_price_diff = float(current_position['10 YR'][5]) - float(current_position['10 YR'][4])

    return (two_weight * two_price_diff) + (ten_weight * ten_price_diff)

def getSPY(start_date, end_date):

    spy_start = str(start_date.year) + '-' + str(start_date.month) + '-' + str(start_date.day)
    spy_end = str(end_date.year) + '-' + str(end_date.month) + '-' + str(end_date.day)

    # Acquire SPY (S&P 500 ETF) data for bench mark
    try:
        # Make request to Quandl for SPY data
        spy = quandl.get('GOOG/NYSE_SPY', start_date=spy_start, end_date=spy_end, collapse='monthly')
        return spy[:]['Close']

    except Exception:
        print('SPY (S&P 500 ETF) retrieval issue. Quitting.')
        print(Exception.__traceback__)
        quit()

def getRF(start_date, end_date):

    rf_start = str(start_date.year) + '-' + str(start_date.month) + '-' + str(start_date.day)
    rf_end  = str(end_date.year) + '-' + str(end_date.month) + '-' + str(end_date.day)

    # Acquire the risk-free rates
    try:
        # Make request to Quandl for treasury yield data
        yields = quandl.get('USTREASURY/YIELD', start_date=rf_start, end_date=rf_end, collapse='monthly')
        return yields[:]['1 MO'] * (1 / 12)

    except Exception:
        print('US Treasury yield retrieval issue. Quitting.')
        print(Exception.__traceback__)
        quit()

def graphData(pnl_arr, spy_arr):

    # Create arrays for X and Y data
    x_data = []
    pnl_data = []
    spy_data = []

    # Go through data sets, matching each date based on traded dates
    for index in range(0, len(pnl_arr)):
        x_data.append(index)
        pnl_data.append(pnl_arr[index][1])
        spy_data.append(spy_arr[pnl_arr[index][0]])

    plot(x_data, pnl_data, label='YC Arb')
    plot(x_data, spy_data, label='SPY')
    legend()
    xlabel('Time (months)')
    ylabel('Value ($)')
    title('P&L Graph of YC Arb and SPY')
    show()

def calcSharpe(rf_arr, pnl_arr):

    # Create temporary array for RF and P&L data for easy calculation
    temp_rf_arr = []
    temp_pnl_arr = []

    # Go through data sets, matching each date based on traded dates
    for index in range(0, len(pnl_arr)):
        temp_pnl_arr.append(pnl_arr[index][1])
        temp_rf_arr.append(rf_arr[pnl_arr[index][0]])

    return (((temp_pnl_arr[len(temp_pnl_arr) - 1] - temp_pnl_arr[0]) / temp_pnl_arr[0]) - temp_rf_arr[len(temp_rf_arr) - 1]) / statistics.stdev(temp_pnl_arr)

if __name__ == '__main__':

    # Set start and end dates
    start = datetime.date(2011, 1, 31)
    end = datetime.date(2016, 12, 31)

    # Acquire SPY data between start and end period
    spy_arr = getSPY(start, end)

    # Define pnl start as beginning SPY value (first trade is 3rd month)
    pnl = spy_arr.iloc[2]
    pnl_arr = []
    first_date = str(spy_arr.index[2].year) + '-' + str(spy_arr.index[2].month) + '-' + str(spy_arr.index[2].day)
    pnl_arr = [[first_date, spy_arr.iloc[2]]]

    # Returns DataFrame with Datetime as yield_index and 6 MO to 30 YR yields
    yield_rates = getYields(start, end)

    # Go through each date and get appropriate 2 YR and 10 YR bonds
    # Define initial historical (1-period) yields
    current_position = {}
    yield_dict = {}
    yield_dict['hist'] = [yield_rates.iloc[0]['2 YR'], yield_rates.iloc[0]['10 YR']]
    for yield_index, yields in yield_rates.iterrows():

        # Set current yield
        yield_dict['current'] = [yields['2 YR'], yields['10 YR']]

        # Set the bond years
        bond_year1 = 2
        bond_year2 = 10

        # Adjust due to '0' added in treasury output
        temp_month = str(yield_index.month)
        if yield_index.month < 10:
            temp_month = '0' + temp_month

        # Look for bonds issues on the 15th of each month
        # Allow for more frequent trading opportunities
        bond_one_date = temp_month + '/' + '15' + '/' + str(yield_index.year + bond_year1)
        bond_two_date = temp_month + '/' + '15' + '/' + str(yield_index.year + bond_year2)

        # Retrieve the table of bond prices
        bond_info_table = retrieveBondInfo(yield_index)

        # Iterate through all of the bonds in table
        bond_one_bool = bond_two_bool = False
        temp_bond_one = temp_bond_two = []
        for tr in bond_info_table.find_all('tr')[1:]: # [1:] to ignore header

            # Assign bond values to an array
            # Array: [0] = CUSIP, [1] = type, [2] = coupon, [3] = maturity, [6] = closing price
            td_arr = tr.find_all('td')

            # Check only for Market Based bonds and notes, not TIPS
            if 'MARKET BASED' in td_arr[1].text:

                # Check if we've found the maturity for the first bond
                if td_arr[3].text == bond_one_date and not bond_one_bool:

                    # Only use the first bond for this maturity
                    # Assign the bond for potential use later
                    bond_one_bool, temp_bond_one = assignFirstBond(td_arr)

                # Else check if we've found the maturity for the second bond
                elif td_arr[3].text == bond_two_date and not bond_two_bool:

                    # Only use the first bond for this maturity
                    # Assign the bond for potential use later
                    bond_two_bool, temp_bond_two = assignFirstBond(td_arr)

                # Check if we are holding a position and add / assign the current price of that bond
                if len(current_position) > 0 and (td_arr[0].text == current_position['2 YR'][0] or
                                                          td_arr[0].text == current_position['10 YR'][0]):

                    # Update the current price based on CUSIP
                    updateCurrentPrice(td_arr, current_position, yields)

        # Conditions for making a trade:
        # 1) 2-Year and 10-Year bonds issued in same month
        # 2) End of testing period
        last_item = yield_index == yield_rates.index[-1]
        both_bond_bool = bond_one_bool and bond_two_bool

        # Test trade conditions are met
        if last_item or both_bond_bool:

            print('Making a trade on ' + str(yield_index.year) + '-' + str(yield_index.month) + '-' + str(yield_index.day) + '.')

            # If we do not have a current position
            if len(current_position) == 0:

                # Assign bond info to dict
                current_position['2 YR'] = temp_bond_one
                current_position['10 YR'] = temp_bond_two

            # If we do have a current position
            else:

                # Calculate the P&L after liquidating the current position
                pnl += calcPNL(current_position)
                pnl_arr.append([str(yield_index.year) + '-' + str(yield_index.month) + '-' + str(yield_index.day), pnl])

                # Update the current position
                current_position['2 YR'] = temp_bond_one
                current_position['10 YR'] = temp_bond_two

        # Update the historical yields
        yield_dict['hist'] = [yields['2 YR'], yields['10 YR']]

    # Cacluate and print Sharpe ratio
    print('Sharpe ratio:', calcSharpe(getRF(start, end), pnl_arr))

    # Graph the P&L of Yield Curve Arb strat vs SPY benchmark
    graphData(pnl_arr, spy_arr)


