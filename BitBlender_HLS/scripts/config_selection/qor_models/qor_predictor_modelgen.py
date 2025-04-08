
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import sklearn.ensemble as sk_ensemble
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error




##################
##################
## CHANGE ME 
##################
##################

TEST_SPLIT_FRACTION = 0.2

##################
##################
##################


def read_training_data(filename):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename)

    # Define the input features (first 5 columns) and the target variables (7th and 8th column)
    # Input features
    htsbm = df.iloc[:, :5]
    # Target variable (bitstream completed)
    xclbin_success_data = df.iloc[:, 7]

    # Get rid of incomplete frequency numbers (those are decided by the "FINISHED" model)
    df2 = df[df.iloc[:,6] != -1]
    # Input features
    htsbm_filtered = df2.iloc[:, :5]
    # Target variable (frequency)
    freq_data = df2.iloc[:, 6]
    
    return (htsbm, xclbin_success_data, htsbm_filtered, freq_data)



def train_and_test_model(xdata, ydata, num_trees, forest_type):
    # Split the data into training and testing sets
    X_train, X_test, Y_train, Y_test = train_test_split(  xdata, 
                                                          ydata, 
                                                          test_size=TEST_SPLIT_FRACTION, random_state=30)
    # Initialize the random forest regressor
    if (forest_type.lower() == "regressor"):
        regressor = sk_ensemble.RandomForestRegressor(n_estimators=num_trees, random_state=42)
    elif (forest_type.lower() == "classifier"):
        regressor = sk_ensemble.RandomForestClassifier(n_estimators=num_trees, random_state=42)
    else:
        return TypeError("unknown forest type")

    # Train the random forest model
    regressor.fit(X_train, Y_train)
    # Make predictions on the test set
    Y_pred = regressor.predict(X_test)

    return (regressor, Y_pred, Y_test)



####################################################################################################################################


if __name__ == "__main__":
    
    (xbitstream_fin_data, ybitstream_fin_data, xfreq_data, yfreq_data) = read_training_data('./qor_data/FreqDataCSV.csv')

    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    """
        THIS is the "Bitstream-Completion Estimator Model", which estimates if the bitstream will be able to complete or not, for a given HTSBM config.
        It's basically a binary classifier on 5 inputs.
    """
    NUM_ESTIMATORS_ARR = range(1,25)
    bitstream_error_dict = {}
    bitstream_models = {}
    for num_estimators in NUM_ESTIMATORS_ARR:
        print("--------------------------------------")
        print("num_estimators = {}".format(num_estimators))
        (bitstream_fin_model, Y_pred, Y_test) = train_and_test_model(xbitstream_fin_data, ybitstream_fin_data, num_estimators, forest_type="classifier")

        y_test_arr = Y_test.values  # Convert pandas dataframe into an array
        badness_rating = 0
        false_positives = 0
        false_negatives = 0
        for i in range(len(Y_pred)):
            rounded_prediction = (1 if (Y_pred[i] > 0.8) else 0)
            if (rounded_prediction != y_test_arr[i]):

                ### Grade false positives more harshly (we think it'll pass P&R but it actually fails)
                if (rounded_prediction == 1):
                    badness_rating += 3
                    false_positives += 1

                elif (rounded_prediction == 0):
                    badness_rating += 1
                    false_negatives += 1

        fail_rate = badness_rating / len(Y_pred)

        print('BITSTREAM COMPLETION model: badness_rating :', badness_rating)
        print('BITSTREAM COMPLETION model: number of tests :', len(Y_pred))
        print('BITSTREAM COMPLETION model: false positives =', false_positives)
        print('BITSTREAM COMPLETION model: false negatives =', false_negatives)
        bitstream_error_dict[num_estimators] = badness_rating
        bitstream_models[num_estimators] = bitstream_fin_model

    min_badness = 9999
    min_badness_key = 0
    for key in bitstream_error_dict:
        if (bitstream_error_dict[key] < min_badness):
            min_badness = bitstream_error_dict[key]
            min_badness_key = key

    print("MINIMIZED at {}".format(min_badness_key))

    BITSTREAM_PREDICTION_MODEL = bitstream_models[min_badness_key]

    with open("bitstream_model.pkl", 'wb') as f:
        pickle.dump(BITSTREAM_PREDICTION_MODEL, f)

    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    """
        THIS is the "Frequency-prediction model", which estimates the frequency achieved by a particular HTSBM config.
        It's a 'normal' regression model, with 5 input variables and a continuous output variable.
    """
    print("\n\n\n\n\n\n")


    NUM_ESTIMATORS_ARR = range(5,50)
    freq_mae_dict = {}
    frequency_models = {}
    for num_estimators in NUM_ESTIMATORS_ARR:
        print("--------------------------------------")
        print("num_estimators = {}".format(num_estimators))
        (freq_model, Y_pred, Y_test) = train_and_test_model(xfreq_data, yfreq_data, num_estimators, forest_type="regressor")

        freq_mae = mean_absolute_error(Y_test, Y_pred)
        freq_max_err = np.max( np.abs(Y_test - Y_pred) )
        print('FREQUENCY model: Mean absolute Error:', freq_mae)
        print('FREQUENCY model: number of tests :', len(Y_pred))
        print('FREQUENCY model: MAX Error:', freq_max_err)
        freq_mae_dict[num_estimators] = freq_mae
        frequency_models[num_estimators] = freq_model

    min_mae = 9999
    min_mae_key = 0
    for key in freq_mae_dict:
        if (freq_mae_dict[key] < min_mae):
            min_mae = freq_mae_dict[key]
            min_mae_key = key

    print("MINIMIZED at {}".format(min_mae_key))

    FREQUENCY_PREDICTION_MODEL = frequency_models[min_mae_key]

    with open("frequency_model.pkl", 'wb') as f:
        pickle.dump(FREQUENCY_PREDICTION_MODEL, f)












