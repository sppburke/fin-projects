import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.decomposition import PCA, KernelPCA, SparsePCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
import time

np.set_printoptions(suppress=True)
np.set_printoptions(precision=9)

def calculate_mse(predictions, actuals):

    mse = 0.0

    for index in range(0, len(predictions)):
        mse += abs(predictions[index] - actuals.iloc[index]) ** 2

    mse = mse / len(predictions)

    return mse

def calculate_regression(type, classifier):

    # Start execution timer
    ts = time.time()

    # Create the relevant PC object (PCA or KPCA)
    if type == 'PCA':
        pca = PCA()
    elif type == 'kPCA':
        pca = KernelPCA(6)
    elif type == 'sPCA':
        pca = SparsePCA()
    else:
        print('Non-compatible regressor requested, now exiting.')
        quit()

    # Create the PCA information for the training data utilizing scaled x call and put data
    call_x_train_pca = pca.fit_transform(call_x_train_scaled)
    put_x_train_pca = pca.fit_transform(put_x_train_scaled)

    # Create the classifier based on input
    if classifier == 'kNN':
        classifier_call = KNeighborsRegressor()
        classifier_put = KNeighborsRegressor()
    elif classifier == 'GB':
        classifier_call = GradientBoostingRegressor()
        classifier_put = GradientBoostingRegressor()
    elif classifier == 'RF':
        classifier_call = RandomForestRegressor()
        classifier_put = RandomForestRegressor()
    else:
        print('Non-compatible regressor requested, now exiting.')
        quit()

    # Fit the x and y training data for calls and puts
    classifier_call.fit(call_x_train_pca, call_y_train)
    classifier_put.fit(put_x_train_pca, put_y_train)

    # Create the PCA information for the test data utilizing scaled x call and put data
    call_x_test_pca = pca.transform(call_x_test_scaled)
    put_x_test_pca = pca.transform(put_x_test_scaled)

    # Predict the implied volatility using kNN
    call_predictions = classifier_call.predict(call_x_test_pca)
    put_predictions = classifier_put.predict(put_x_test_pca)

    # Calculate and display mean squared error
    call_mse = calculate_mse(call_predictions, call_y_test)
    put_mse = calculate_mse(put_predictions, put_y_test)

    # Print corresponding MSE for calls and puts basd on regression
    print('\n{} {} Call MSE: {:f}'.format(type, classifier, call_mse))
    print('{} {} Put MSE: {:f}'.format(type, classifier, put_mse))

    # Print out execution time
    print('Execution Duration: {:f} seconds'.format(time.time() - ts))

if __name__ == '__main__':

    # Read the call and put options data from CSV file
    call_options_data = pd.read_csv('myOptionCallData.csv', skiprows=1, header=None)
    put_options_data = pd.read_csv('myOptionPutData.csv', skiprows=1, header=None)

    # Add column headers for further reference
    call_options_data.columns = ['Stock Price', 'Strike Price', 'Time to Maturity', 'Interest Rate', 'Option Price',
                                 'Option Type', 'Volatility', 'Implied Volatility']
    put_options_data.columns = ['Stock Price', 'Strike Price', 'Time to Maturity', 'Interest Rate', 'Option Price',
                                'Option Type', 'Volatility', 'Implied Volatility']

    # Separate the call and put options data into x and y components
    call_x, call_y = call_options_data.iloc[:, :6], call_options_data.iloc[:, 7]
    put_x, put_y = put_options_data.iloc[:, :6], put_options_data.iloc[:, 7]

    # Split the x and y components into test and training for call and put data
    call_x_train, call_x_test, call_y_train, call_y_test = train_test_split(call_x, call_y, test_size=0.2, random_state=14)
    put_x_train, put_x_test, put_y_train, put_y_test = train_test_split(put_x, put_y, test_size=0.2, random_state=14)

    # Scale the test and training x components for call and put data
    call_x_train_scaled = StandardScaler().fit_transform(call_x_train)
    call_x_test_scaled = StandardScaler().fit_transform(call_x_test)
    put_x_train_scaled = StandardScaler().fit_transform(put_x_train)
    put_x_test_scaled = StandardScaler().fit_transform(put_x_test)

    # Print out size dimensions for call and put test and training data
    print('Call X Training Size: ', len(call_x_train))
    print('Call Y Training Size: ', len(call_y_train))
    print('Call X Test Size: ', len(call_x_test))
    print('Call Y Test Size: ', len(call_y_test))
    print('Put X Training Size: ', len(put_x_train))
    print('Put Y Training Size: ', len(put_y_train))
    print('Put X Test Size:', len(put_x_test))
    print('Put Y Test Size: ', len(put_y_test))

    # Calculate and evaluate the PCA kNN regression
    calculate_regression('PCA', 'kNN')

    # Calculate and evaluate the KPCA kNN regression
    calculate_regression('kPCA', 'kNN')

    # Calculate and evaluate the sPCA kNN regression
    calculate_regression('sPCA', 'kNN')

    # Calculate and evaluate the PCA GB regression
    calculate_regression('PCA', 'GB')

    # Calculate and evaluate the KPCA GB regression
    calculate_regression('kPCA', 'GB')

    # Calculate and evaluate the sPCA GB regression
    calculate_regression('sPCA', 'GB')

    # Calculate and evaluate the PCA RF regression
    calculate_regression('PCA', 'RF')

    # Calculate and evaluate the KPCA RF regression
    calculate_regression('kPCA', 'RF')

    # Calculate and evaluate the sPCA RF regression
    calculate_regression('sPCA', 'RF')