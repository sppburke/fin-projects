import quandl
import statistics as stat
import numpy as np
from pylab import xlabel, ylabel, title, plot, show, legend

quandl.ApiConfig.api_key = ''

def getSPY(test_start, test_end):

    # Acquire SPY (S&P 500 ETF) data for bench mark
    try:
        # Make request to Quandl for SPY data
        spy = quandl.get('GOOG/NYSE_SPY', start_date=test_start, end_date=test_end, collapse='monthly')
        return spy[:]['Close']

    except Exception:
        print('SPY (S&P 500 ETF) retrieval issue. Quitting.')
        print(Exception.with_traceback())
        quit()

def getRF(start_date, end_date):

    # Acquire the risk-free rates
    try:
        # Make request to Quandl for treasury yield data
        yields = quandl.get('USTREASURY/YIELD', start_date=start_date, end_date=end_date, collapse='monthly')
        return yields[:]['1 MO'] * (1 / 12)

    except Exception:
        print('US Treasury yield retrieval issue. Quitting.')
        print(Exception.with_traceback())
        quit()

def graphData(pnl_arr, spy_arr):

    # Create arrays for X data
    x_data = [i for i in range(0, len(spy_arr))]

    plot(x_data, pnl_arr, label='Crack Spread')
    plot(x_data, spy_arr, label='SPY')
    legend()
    xlabel('Time (months)')
    ylabel('Value ($)')
    title('P&L Graph of Crack Spread and SPY')
    show()

def calcSharpe(rf_arr, pnl_arr):

    return (((pnl_arr[len(pnl_arr) - 1] - pnl_arr[0]) / pnl_arr[0]) - rf_arr[len(rf_arr) - 1]) / stat.stdev(pnl_arr)

def get_historical_data(ticker, start, end):

    return quandl.get(ticker, start_date=start, end_date=end, collapse='monthly')

def get_initial_ema(start, end):

    # Get training settle prices for WTI, RBOB, and ULSD
    df_wti_train = get_historical_data('CHRIS/CME_CL1.6', start, end)
    df_rbob_train = get_historical_data('CHRIS/CME_RB1.6', start, end)
    df_ulsd_train = get_historical_data('CHRIS/CME_HO1.6', start, end)

    # Calculate the spread across historical months
    spread_arr = []
    for index in range(0, len(df_wti_train.index)):

        # Assign individual settle prices
        wti = float(df_wti_train.values[index])
        rbob = float(df_rbob_train.values[index])
        ulsd = float(df_ulsd_train.values[index])

        # Calculate 3:2:1 spread
        spread = (-1 * wti) + ((2 / 3) * rbob * 42) + ((1 / 3) * ulsd * 42)
        spread_arr = np.append(spread_arr, spread)

    # Calcluate the EMA smoothing constant
    multiplier = (2 / (len(spread_arr) + 1))

    return stat.mean(spread_arr), multiplier, spread_arr

def update_ema(ema, multiplier, spread_arr, spread):

    # Update the EMA for a moving 12 month window
    ema = ((spread - ema) * multiplier) + ema

    # The spread array is a moving window
    spread_arr = np.delete(spread_arr, 0)
    spread_arr = np.append(spread_arr, spread)

    # Historical volatility is of the moving window
    sigma = np.std(spread_arr)

    return ema, sigma, spread_arr

if __name__ == '__main__':

    # Two year rolling average window
    train_start = '2013-01-1'
    train_end = '2013-12-31'
    test_start = '2014-01-1'
    test_end = '2016-12-31'

    entry_mult = .75
    exit_mult = .35

    # Retrieve initial spread data and calculate sigma
    ema, multiplier, spread_arr = get_initial_ema(train_start, train_end)

    # Get test settle prices for WTI, RBOB, and ULSD
    df_wti_test = get_historical_data('CHRIS/CME_CL1.6', test_start, test_end)
    df_rbob_test = get_historical_data('CHRIS/CME_RB1.6', test_start, test_end)
    df_ulsd_test = get_historical_data('CHRIS/CME_HO1.6', test_start, test_end)

    # Acquire SPY data between test start and end period
    spy_arr = getSPY(test_start, test_end)

    # Iterate over test data to calculate P&L
    current_position = []
    pnl = spy_arr[0]
    pnl_arr = []
    for index in range(0, len(df_wti_test)):

        # Assign individual settle prices
        wti = float(df_wti_test.values[index])
        rbob = float(df_rbob_test.values[index])
        ulsd = float(df_ulsd_test.values[index])

        # Calculate 3:2:1 spread
        spread = (-1 * wti) + ((2 / 3) * rbob * 42) + ((1 / 3) * ulsd * 42)

        # Update EMA, sigma, and the spread array
        ema, sigma, spread_arr = update_ema(ema, multiplier, spread_arr, spread)

        # If we currently do not have a position
        if len(current_position) == 0:

            # If the current spread is adequately larger than historical spread
            # Short spread
            if (spread > (ema + entry_mult * sigma)):
                current_position = [wti, (2 / 3) * rbob * -42, (1 / 3) * ulsd * -42]

            # If current spread is adequately lower than historical spread
            # Long spread
            elif (spread < (ema - entry_mult * sigma)):
                current_position = [-1 * wti, (2 / 3) * rbob * 42, (1 / 3) * ulsd * 42]

        # Else we do have a position
        else:

            # Exit position if:
            # 1) The spread is below .35 * sigma
            # 2) We've reached the end of the testing data
            if (abs(spread - ema) < exit_mult * sigma) or (index == len(df_wti_test) - 1):

                # Check if long or short spread
                # Unload long spread
                wti_diff = rbob_diff = ulsd_diff = 0.0
                if current_position[0] < 0:

                    # Calculate individual differences
                    wti_diff = ((-1 * wti) - current_position[0]) / abs(current_position[0])
                    rbob_diff = (((2 / 3) * rbob * 42) - current_position[1]) / abs(current_position[1])
                    ulsd_diff = (((1 / 3) * ulsd * 42) - current_position[2]) / abs(current_position[2])

                    current_position = []

                # Unload short spread
                else:

                    wti_diff = (wti - current_position[0]) / abs(current_position[0])
                    rbob_diff = (((2 / 3) * rbob * -42) - current_position[1]) / abs(current_position[1])
                    ulsd_diff = (((1 / 3) * ulsd * -42) - current_position[2]) / abs(current_position[2])

                    current_position = []

                # Calculate current P&L
                pnl *= (1 + wti_diff + rbob_diff + ulsd_diff)

        # Update the running P&L
        pnl_arr.append(pnl)

    # Calculate and print Sharpe ratio
    print('Sharpe Ratio:', calcSharpe(getRF(test_start, test_end), pnl_arr))

    # Graph the P&L of Crack Spread strat vs SPY benchmark
    graphData(pnl_arr, spy_arr)
