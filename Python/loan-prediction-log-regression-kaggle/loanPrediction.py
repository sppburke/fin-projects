from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA, SparsePCA

np.set_printoptions(suppress=True)
np.set_printoptions(precision=5)

def calculate_mse(predictions, actuals):

    mse = 0.0

    for index in range(0, len(predictions)):
        mse += abs(predictions[index] - actuals.iloc[index]) ** 2

    mse = mse / len(predictions)

    return mse

def get_training_testing_data(raw_data_loc):

    # Import the data and assign it to a Dataframe
    pd_raw_data = pd.read_csv(raw_data_loc, header=None)

    # Create accurate column header names
    pd_raw_data.columns = ['Num', 'Delinquency', 'Revolving Credit Percentage', 'Capital Reserves', 'Num Late 60',
                           'Debt Ratio', 'Monthly Income', 'Num Credit Lines', 'Num Late Past 90', 'Num Real Estate',
                           'Num Late 90', 'Num Employees']

    # Remove all rows with 'NaN' in value
    pd_clean_data = pd_raw_data.dropna(how='any')

    # Split into X and Y values
    loan_data_x, loan_data_y = pd_clean_data.iloc[:, 2:], pd_clean_data.iloc[:, 1]

    # Split into traning / testing data for X and Y coordinates
    # 80% training data and 20% testing data
    return train_test_split(loan_data_x, loan_data_y, test_size=0.2, random_state=42)

def getAnswer(credit_prediction):

    if int(credit_prediction) == 0:
        return 'Give Julio credit.'
    else:
        return 'Do not give Julio credit.'

if __name__ == '__main__':

    # Define the data set location
    raw_data_loc = 'credit-info.csv'

    # Split the raw data set into training and testing X and Y components
    training_x, testing_x, training_y, testing_y = get_training_testing_data(raw_data_loc)

    # Scale the training and testing X components
    training_x_scaled = StandardScaler().fit_transform(training_x)
    testing_x_scaled = StandardScaler().fit_transform(testing_x)

    # Create the regressors
    lr_classifier = LogisticRegression(random_state=42)
    lr_pca_classifier = LogisticRegression(random_state=42)
    lr_spca_classifier = LogisticRegression(random_state=42)

    mlp_classifier = MLPClassifier(random_state=42)
    mlp_pca_classifier = MLPClassifier(random_state=42)
    mlp_spca_classifier = MLPClassifier(random_state=42)

    # Create and fit / transform PCA and SPCA data
    pca = PCA()
    spca = SparsePCA()

    training_x_pca = pca.fit_transform(training_x_scaled)
    training_x_spca = spca.fit_transform(training_x_scaled)

    testing_x_pca = pca.fit_transform(testing_x_scaled)
    testing_x_spca = spca.fit_transform(testing_x_scaled)

    # Train the classifiers
    lr_classifier.fit(training_x_scaled, training_y)
    lr_pca_classifier.fit(training_x_pca, training_y)
    lr_spca_classifier.fit(training_x_spca, training_y)

    mlp_classifier.fit(training_x_scaled, training_y)
    mlp_pca_classifier.fit(training_x_pca, training_y)
    mlp_spca_classifier.fit(training_x_spca, training_y)

    # Normal predictions
    lr_predictions = lr_classifier.predict(testing_x_scaled)
    lr_predictions_pca = lr_pca_classifier.predict(testing_x_pca)
    lr_predictions_spca = lr_spca_classifier.predict(testing_x_spca)

    mlp_predictions = mlp_classifier.predict(testing_x_scaled)
    mlp_predictions_pca = mlp_pca_classifier.predict(testing_x_pca)
    mlp_predictions_spca = mlp_spca_classifier.predict(testing_x_spca)

    # Probability predictions
    lr_proba_predictions = lr_classifier.predict_proba(testing_x_scaled)
    lr_proba_predictions_pca = lr_classifier.predict_proba(testing_x_pca)
    lr_proba_predictions_spca = lr_classifier.predict_proba(testing_x_spca)

    mlp_proba_predictions = mlp_classifier.predict_proba(testing_x_scaled)
    mlp_proba_predictions_pca = mlp_classifier.predict_proba(testing_x_pca)
    mlp_proba_predictions_spca = mlp_classifier.predict_proba(testing_x_spca)

    # Compare accuracy of predictions to actuals
    lr_accuracy = lr_classifier.score(testing_x_scaled, testing_y)
    lr_accuracy_pca = lr_classifier.score(testing_x_pca, testing_y)
    lr_accuracy_spca = lr_classifier.score(testing_x_spca, testing_y)

    mlp_accuracy = mlp_classifier.score(testing_x_scaled, testing_y)
    mlp_accuracy_pca = mlp_classifier.score(testing_x_pca, testing_y)
    mlp_accuracy_spca = mlp_classifier.score(testing_x_spca, testing_y)

    # Print the logistic regression coefficients
    print('Coefficients', lr_classifier.coef_)
    print('Intercept', lr_classifier.intercept_)

    # Print out accuracy of model in percentage
    print('Accuracy of Logistic Regression model: {:.2f}%'.format(lr_accuracy * 100))
    print('Accuracy of Logistic Regression with PCA model: {:.2f}%'.format(lr_accuracy_pca * 100))
    print('Accuracy of Logistic Regression with SPCA model: {:.2f}%'.format(lr_accuracy_spca * 100))

    print('Accuracy of Multi-Layer Perceptron model: {:.2f}%'.format(mlp_accuracy * 100))
    print('Accuracy of Multi-Layer Perceptron with PCA model: {:.2f}%'.format(mlp_accuracy_pca * 100))
    print('Accuracy of Multi-Layer Perceptron with SPCA model: {:.2f}%'.format(mlp_accuracy_spca * 100))

    # Acquire and print MSE for all regressors and classifiers
    lr_mse = calculate_mse(lr_predictions, testing_y)
    lr_mse_pca = calculate_mse(lr_predictions_pca, testing_y)
    lr_mse_spca = calculate_mse(lr_predictions_spca, testing_y)

    mlp_mse = calculate_mse(mlp_predictions, testing_y)
    mlp_mse_pca = calculate_mse(mlp_predictions_pca, testing_y)
    mlp_mse_spca = calculate_mse(mlp_predictions_spca, testing_y)

    print('MSE of Logistic Regression model: {:f}'.format(lr_mse))
    print('MSE of Logistic Regression with PCA model: {:f}'.format(lr_mse_pca))
    print('MSE of Logistic Regression with SPCA model: {:f}'.format(lr_mse_spca))

    print('MSE of MLP model: {:f}'.format(mlp_mse))
    print('MSE of MLP with PCA model: {:f}'.format(mlp_mse_pca))
    print('MSE of MLP with SPCA model: {:f}'.format(mlp_mse_spca))

    # Print Julio's info
    print('Julio Info:')
    print(testing_x.iloc[len(testing_x) - 1])

    # Print relevant default probability
    lr_prob = float(lr_proba_predictions[len(testing_x) - 1][1])
    lr_prob_pca = float(lr_proba_predictions_pca[len(testing_x) - 1][1])
    lr_prob_spca = float(lr_proba_predictions_spca[len(testing_x) - 1][1])

    mlp_prob = float(mlp_proba_predictions[len(testing_x) - 1][1])
    mlp_prob_pca = float(mlp_proba_predictions_pca[len(testing_x) - 1][1])
    mlp_prob_spca = float(mlp_proba_predictions_spca[len(testing_x) - 1][1])

    print('Julio LR Default Probability: {:.2f}%'.format(lr_prob * 100))
    print('Julio LR with PCA Default Probability: {:.2f}%'.format(lr_prob_pca * 100))
    print('Julio LR with SPCA Default Probability: {:.2f}%'.format(lr_prob_spca * 100))

    print('Julio MLP Default Probability: {:.2f}%'.format(mlp_prob * 100))
    print('Julio MLP with PCA Default Probability: {:.2f}%'.format(mlp_prob_pca * 100))
    print('Julio MLP with SPCA Default Probability: {:.2f}%'.format(mlp_prob_spca * 100))

    # Print credit answers
    print('Julio Answer (using Logistic Regression):')
    print(getAnswer(lr_predictions[len(testing_x) - 1]))
    print('Julio Answer (using Logistic Regression with PCA):')
    print(getAnswer(lr_predictions_pca[len(testing_x) - 1]))
    print('Julio Answer (using Logistic Regression with SPCA):')
    print(getAnswer(lr_predictions_spca[len(testing_x) - 1]))

    print('Julio Answer (using MLP Benchmark):')
    print(getAnswer(mlp_predictions[len(testing_x) - 1]))
    print('Julio Answer (using MLP Benchmark with PCA):')
    print(getAnswer(mlp_predictions_pca[len(testing_x) - 1]))
    print('Julio Answer (using MLP Benchmark with SPCA):')
    print(getAnswer(mlp_predictions_spca[len(testing_x) - 1]))