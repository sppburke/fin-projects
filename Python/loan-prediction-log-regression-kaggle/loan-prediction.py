from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

np.set_printoptions(suppress=True)
np.set_printoptions(precision=5)

def get_training_testing_data(raw_data_loc):

    # Import the data and assign it to a Dataframe
    pd_raw_data = pd.read_csv(raw_data_loc, skiprows=1, header=None)

    # Create accurate column header names
    pd_raw_data.columns = ['Num', 'Delinquency', 'Revolving Credit Percentage', 'Years Old', 'Num Late 60', 'Debt Ratio',
                           'Monthly Income', 'Num Credit Lines', 'Num Late Past 90', 'Num Real Estate',
                           'Num Late 90', 'Num Employees']

    # Remove all rows with 'NaN' in value
    pd_clean_data = pd_raw_data.dropna(how='any')

    # Split into X and Y values
    loan_data_x, loan_data_y = pd_clean_data.iloc[:, 2:], pd_clean_data.iloc[:, 1]

    # Split into traning / testing data for X and Y coordinates
    # 80% training data and 20% testing data
    return train_test_split(loan_data_x, loan_data_y, test_size=0.2)


if __name__ == '__main__':

    # Define the data set location
    raw_data_loc = 'credit-info.csv'

    # Split the raw data set into training and testing X and Y components
    training_x, testing_x, training_y, testing_y = get_training_testing_data(raw_data_loc)

    # Create and assign data to Logistic Regression
    lr_classifier = LogisticRegression()
    call_x_train_scaled = lr_classifier.fit(training_x, training_y)

    # Predict the testing data
    predictions = lr_classifier.predict(testing_x)

    # Compare accuracy of predictions to actuals
    accuracy = lr_classifier.score(testing_x, testing_y)

    # Print out accuracy of model in percentage
    print('Accuracy of model: {:.2f}%'.format(accuracy * 100))