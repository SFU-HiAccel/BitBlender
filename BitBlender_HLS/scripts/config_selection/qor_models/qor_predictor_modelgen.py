
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import sklearn.ensemble as sk_ensemble
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from statistics import fmean

#import matplotlib.pyplot as plt

from enum import Enum, auto

##################
##################
## CHANGE ME 
##################
##################

TEST_SPLIT_FRACTION = 0.2

##################
##################
##################

class ForestType(Enum):
    REGRESSOR = 1
    CLASSIFIER = 2




class Features(Enum):
    bitblnd_cfg                 = auto()
    allresource_raw             = auto()
    logicresource_raw           = auto()
    memresource_raw             = auto()
    xclbinsuccess               = auto()

    passonly_bitblnd_cfg        = auto()
    passonly_allresource_raw    = auto()
    passonly_frequency          = auto()

    allresource_pct             = auto()
    logicresource_pct           = auto()
    memresource_pct             = auto()
    passonly_allresource_pct    = auto()

    ESTIMATED_allresource_pct   = auto()
    passonly_ESTIMATED_allresource_pct   = auto()







def read_training_data(filename, features, test_fraction):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename)
    # Remove the rows that failed for an anomalous reason
    df = df[df.iloc[:,0] == 0]

    print("\n\n\nALL OF OUR DATA:")
    print(df)

    if (features == 0):
        bbcfg_cols = [1, 2, 3, 4, 5, 8, 9]
    elif (features == 1):
        bbcfg_cols = [1, 2, 3, 4, 5]
    elif (features == 2):
        bbcfg_cols = [4, 8, 9]

    allresource_raw_cols     = [14,15,16,17,18]
    logicresource_raw_cols   = [14,15,18]
    memresource_raw_cols     = [16,17]
    xclbin_success_col   = 13
    freq_col             = 12

    ###############################################
    ### Split the data into PASSING builds, and FAILING builds.
    ###############################################
    passonly_data = df[df.iloc[:, xclbin_success_col] == 1]
    failonly_data = df[df.iloc[:, xclbin_success_col] == 0]

    if (test_fraction < 1.0):
        (pass_train, pass_test) = train_test_split(
                passonly_data
                ,test_size = test_fraction
                ,random_state=30
            )
        (fail_train, fail_test) = train_test_split(
                failonly_data
                ,test_size = test_fraction
                ,random_state=30
            )
    elif (test_fraction >= 1.0):
        print("\n\n\n\n\n\n\n\n\n\nWARNING! WARNING! WARNING! WARNING! WARNING!")
        print("DUPLICATING THE DATA into training and test datasets.\n\n\n\n\n")
        pass_test = passonly_data
        fail_test = failonly_data
        pass_train = pass_test
        fail_train = fail_test

    print("{} passing builds".format( passonly_data.shape[0] ))
    print("{} failed  builds".format( failonly_data.shape[0] ))

    train_rows = pd.concat(objs=(pass_train, fail_train))
    test_rows  = pd.concat(objs=(pass_test, fail_test))

    print("\n\n\nALL OF THE TRAINING DATA:\n")
    print(train_rows)
    print("\n\n\nALL OF THE TESTING DATA:\n")
    print(test_rows)

    data = {}
    data["train"] = {}
    data["test"] = {}

    ### Define the input features and the target variables
    data["train"][Features.bitblnd_cfg]         = train_rows.iloc[:, bbcfg_cols]
    data["test"][Features.bitblnd_cfg]          = test_rows.iloc [:, bbcfg_cols]

    data["train"][Features.allresource_raw]     = train_rows.iloc[:, allresource_raw_cols]
    data["test"][Features.allresource_raw]      = test_rows.iloc [:, allresource_raw_cols]

    data["train"][Features.logicresource_raw]   = train_rows.iloc[:, logicresource_raw_cols]
    data["test"][Features.logicresource_raw]    = test_rows.iloc [:, logicresource_raw_cols]

    data["train"][Features.memresource_raw]     = train_rows.iloc[:, memresource_raw_cols]
    data["test"][Features.memresource_raw]      = test_rows.iloc [:, memresource_raw_cols]

    data['train'][Features.xclbinsuccess]       = train_rows.iloc[:, xclbin_success_col]
    data['test'][Features.xclbinsuccess]        = test_rows.iloc [:, xclbin_success_col]

    ### Filter out the rows in which the design failed to build.
    filtered_train  = train_rows[train_rows.iloc[:,xclbin_success_col] != 0]
    filtered_test   = test_rows [test_rows.iloc [:,xclbin_success_col] != 0]

    data['train'][Features.passonly_bitblnd_cfg]    = filtered_train.iloc[:, bbcfg_cols]
    data['test'][Features.passonly_bitblnd_cfg]     = filtered_test.iloc [:, bbcfg_cols]

    data['train'][Features.passonly_allresource_raw]= filtered_train.iloc[:, allresource_raw_cols]
    data['test'][Features.passonly_allresource_raw] = filtered_test.iloc [:, allresource_raw_cols]

    data['train'][Features.passonly_frequency]      = filtered_train.iloc[:, freq_col]
    data['test'][Features.passonly_frequency]       = filtered_test.iloc [:, freq_col]


    ### Convert the raw resources into percentage resources
    data['train'][Features.allresource_pct]             = convert_resources_raw_to_pcts(data['train'][Features.allresource_raw])
    data['test'][Features.allresource_pct]              = convert_resources_raw_to_pcts(data['test'][Features.allresource_raw])

    if (logicresource_raw_cols != [14,15,18] or memresource_raw_cols != [16,17]):
        raise AssertionError("KENNY - your column numberings may be out of date.")
    else:
        data['train'][Features.logicresource_pct]           = data['train'][Features.allresource_pct].iloc[:, [0,1,4]]
        data['test'][Features.logicresource_pct]            = data['test'][Features.allresource_pct].iloc[:, [0,1,4]]

        data['train'][Features.memresource_pct]             = data['train'][Features.allresource_pct].iloc[:, [2,3]]
        data['test'][Features.memresource_pct]              = data['test'][Features.allresource_pct].iloc[:, [2,3]]

    data['train'][Features.passonly_allresource_pct]    = convert_resources_raw_to_pcts(data['train'][Features.passonly_allresource_raw])
    data['test'][Features.passonly_allresource_pct]     = convert_resources_raw_to_pcts(data['test'][Features.passonly_allresource_raw])


    #print("\n\n\n\nDEBUGGING NOW:\n")
    #print(data['train'][Features.allresource_raw])
    #print(data['train'][Features.allresource_pct])
    #print(data['train'][Features.logicresource_pct])
    #print(data['train'][Features.memresource_pct])
    #raise AssertionError("earlyexit")


    #mname = "pearson"       ### Standard "linear" correlation calculation.
    #mname = "spearman"     ### Correlating the RANKINGS of the data (after sorting)
    #data_corr = df.corr(method=mname)
    #plt.matshow(data_corr)
    #plt.show()
    #df2 = df[df.iloc[:,freq_col] != -1]
    #data_corr = df2.corr(method=mname)
    #plt.matshow(data_corr)
    #plt.show()

    return data






def convert_resources_raw_to_pcts(
    raw_resource_data
    ,fpga_resources_dict = {"kLUT": 1304, "kFF": 2607, "BRAM": 2016, "URAM": 960, "DSP": 9024}
):
    """
    INPUTS:
        raw_resource_data:
            a pandas DataFrame object, with columns defined as
            [kLUT, kFF, BRAM, URAM, DSP]. Represents the raw # of each resource used.
        fpga_resources_dict:
            a dict, with keys "kLUT", "kFF", "BRAM", "URAM", and "DSP".
            Represents the available number of resources, on a given FPGA.
    OUTPUTS:
        percent_resource_data:
            a pandas DataFrame object, with columns defined as
            [%LUT, %FF, %BRAM, %URAM, %DSP].
    """
    #print("\n\n\nRAW RESOURCE DATA:")
    #print(raw_resource_data)

    percent_resource_data = pd.DataFrame(raw_resource_data)

    for rname in ["kLUT", "kFF", "BRAM", "URAM", "DSP"]:
        percent_resource_data[rname] = percent_resource_data[rname].div(fpga_resources_dict[rname])

    percent_resource_data.rename(columns={
            "kLUT"  : "%LUT"
            ,"kFF"  : "%FF"
            ,"BRAM" : "%BRAM"
            ,"URAM" : "%URAM"
            ,"DSP"  : "%DSP"
        }
        ,inplace=1
    )

    #print("\n\nPERCENTAGE RESOURCE DATA:")
    #print(percent_resource_data)

    return percent_resource_data






def train_and_test_model(
    data, infeatures, outfeatures, num_trees,
    forest_type, num_output_columns, do_print
):
    ## Explicitly create a copy, so we don't modify the original data dictionary.
    X_train = pd.DataFrame(data['train'] [infeatures]   )
    X_test  = pd.DataFrame(data['test']  [infeatures]   )

    if (num_output_columns == 1):
        Y_train = pd.Series(data['train'] [outfeatures]  )
        Y_test  = pd.Series(data['test']  [outfeatures]  )
    else:
        Y_train = pd.DataFrame(data['train'] [outfeatures]  )
        Y_test  = pd.DataFrame(data['test']  [outfeatures]  )

    ###############################
    ###############################
    ###############################

    if (do_print):
        print("THE X TEST DATA IS:")
        print(X_test)
        print("\n\n\n")
        print("THE Y TEST DATA IS:")
        print(Y_test)

        if (forest_type == ForestType.REGRESSOR):
            print("\n\nTRAINING DATA STATISTICS:")
            print("     #points = {}".format(len(Y_train)))
            print("     min     = {}".format(Y_train.min()))
            print("     max     = {}".format(Y_train.max()))
            print("     mean    = {}".format(Y_train.mean()))
            print("     var     = {}".format(Y_train.var()))

            print("\n\nTESTING DATA STATISTICS:")
            print("     #points = {}".format(len(Y_test)))
            print("     min     = {}".format(Y_test.min()))
            print("     max     = {}".format(Y_test.max()))
            print("     mean    = {}".format(Y_test.mean()))
            print("     var     = {}".format(Y_test.var()))

        elif (forest_type == ForestType.CLASSIFIER):
            print("#Train points = {}, #pass = {}, #fail = {}".format(
                        len(Y_train)
                        ,Y_train.sum()
                        ,len(Y_train)-Y_train.sum()
                    )
            )
            print("#Test points  = {}, #pass = {}, #fail = {}".format(
                        len(Y_test)
                        ,Y_test.sum()
                        ,len(Y_test)-Y_test.sum()
                    )
            )
        print("\n\n\n")

    ###############################
    ###############################
    ###############################


    # Initialize the random forest
    if (forest_type == ForestType.REGRESSOR):
        predictor_model = sk_ensemble.RandomForestRegressor(n_estimators=num_trees, random_state=42)
    elif (forest_type == ForestType.CLASSIFIER):
        predictor_model = sk_ensemble.RandomForestClassifier(n_estimators=num_trees, random_state=42)
    else:
        raise ValueError("The requested ForestType is unknown.")

    # Train the random forest model
    predictor_model.fit(X_train, Y_train)
    # Make predictions on the test set
    Y_pred = predictor_model.predict(X_test)

    ################################################
    ## Print out the tests that failed.
    if (forest_type == ForestType.REGRESSOR):
        comparison = (abs(Y_pred/Y_test) < 1.05)
    elif (forest_type == ForestType.CLASSIFIER):
        comparison = (Y_test == Y_pred)
    else:
        raise ValueError("The requested ForestType is unknown.")

    fail_rows = comparison[comparison == False].index.tolist()

    print("\n\n Y-value shapes:")
    print(Y_train.shape)
    print(Y_test.shape)
    print(Y_pred.shape)
    if (num_output_columns == 1):
        Y_train = Y_train.to_frame("target_result")
        Y_test = Y_test.to_frame("target_result")
        Y_pred = np.reshape(Y_pred, (-1, 1))
        print(Y_train.shape)
        print(Y_test.shape)
        print(Y_pred.shape)



    ## Convert from pandas df to a numpy array.
    Y_test = Y_test.to_numpy()

    for outcol in range(0, num_output_columns):
        X_test["Predicted {}".format(outcol)] = Y_pred[:, outcol]
        X_test["Actual {}".format(outcol)] = Y_test[:, outcol]
        if (forest_type == ForestType.REGRESSOR):
            X_test["Diff {}".format(outcol)] = abs(Y_pred[:, outcol] - Y_test[:, outcol])

    failed_tests = X_test.loc[fail_rows]
    print("\n\n\n THE FAILED TESTS (>5%) ARE:")
    print(failed_tests)
    ################################################

    return (predictor_model, Y_pred, Y_test)













def train_resource_estimators(
    data
    ,num_output_columns
):
    """
        THIS is the "resource-prediction model", which estimates the resources of an HTSBM config.
        It's a regression model, with 5 input variables and
        ${num_output_columns} continuous output variables.
    """
    print("\n\n\n\n\n\n PREDICTING RESOURCE USAGES NOW")

    if (num_output_columns == 5):
        target_columns = Features.allresource_raw
    elif (num_output_columns == 3):
        target_columns = Features.logicresource_raw
    elif (num_output_columns == 2):
        target_columns = Features.memresource_raw

    ### AS OF FEB15, the goal is to test out different model architectures.
    ### Right now I'm profiling having one model which predicts ALL the resources, one that only does logic resources (LUT/FF/DSP), and one that only does memory resources (BRAM/URAM)
    NUM_ESTIMATORS_ARR = [6,8,10,12,14,16,18,20,22,24,26,28,30]
    resource_mae_dict = {}
    resource_est_models = {}
    for num_estimators in NUM_ESTIMATORS_ARR:
        print("--------------------------------------")
        print("num_estimators = {}".format(num_estimators))
        (resource_predictor_model, Y_pred, Y_test) = train_and_test_model(
                #x_all_bitblnd_cfgs
                #,resource_data
                data
                ,Features.bitblnd_cfg
                ,target_columns
                ,num_estimators
                ,forest_type=ForestType.REGRESSOR
                ,num_output_columns = num_output_columns
                ,do_print = (num_estimators == NUM_ESTIMATORS_ARR[0])
            )

        mae_values = mean_absolute_error(Y_test, Y_pred, multioutput="raw_values")
        max_errors = list(range(0, num_output_columns))
        for i in range(0, num_output_columns):
            print('RESOURCE EST model: column {} Mean absolute Error: {}'.format(i, mae_values[i]))

        print('RESOURCE EST model: number of tests :', len(Y_pred))

        max_errors = np.max( np.abs(Y_test - Y_pred), axis=0 )
        for i in range(0, num_output_columns):
            print('RESOURCE EST model: MAX Error column {}: {}'.format(i, max_errors[i]))

        resource_mae_dict[num_estimators] = mae_values
        resource_est_models[num_estimators] = resource_predictor_model

    min_average_mae = 9999
    min_average_mae_key = 0
    for key in resource_mae_dict:
        ### We have mean-absolute-errors for kLUT, kFF, BRAM, URAM, DSP.
        ### Here, we average these mean-absolute-errors.
        print(resource_mae_dict[key])
        average_mae = fmean(resource_mae_dict[key])

        if (average_mae < min_average_mae):
            min_average_mae = average_mae
            min_average_mae_key = key

    print("MINIMIZED at {}".format(min_average_mae_key))

    RESOURCE_EST_MODEL = resource_est_models[min_average_mae_key]

    if (num_output_columns == 5):
        with open("models/resource_estimation_model_allinone.pkl", 'wb') as f:
            pickle.dump(RESOURCE_EST_MODEL, f)
    elif (num_output_columns == 3):
        with open("models/resource_estimation_model_logicresources.pkl", 'wb') as f:
            pickle.dump(RESOURCE_EST_MODEL, f)
    elif (num_output_columns == 2):
        with open("models/resource_estimation_model_memoryresources.pkl", 'wb') as f:
            pickle.dump(RESOURCE_EST_MODEL, f)
















def generate_all_resource_estimates( orig_data ):
    """
    THIS FUNCTION takes in the unmodified data dictionary, and adds columns
    corresponding to the estimated % resource usages, as predicted by the resource-estimator models.
    """
    data = dict(orig_data)

    with open("models/resource_estimation_model_logicresources.pkl", 'rb') as modelfile:
        logic_resources_estimator = pickle.load(modelfile)
    with open("models/resource_estimation_model_memoryresources.pkl", 'rb') as modelfile:
        memory_resources_estimator = pickle.load(modelfile)

    for feature in [Features.bitblnd_cfg, Features.passonly_bitblnd_cfg]:
        for t in ['train', 'test']:
            inputs    = pd.DataFrame(data[t][feature])
            predicted_logic   = logic_resources_estimator.predict (inputs)
            predicted_mem     = memory_resources_estimator.predict(inputs)
            predicted_logic   = pd.DataFrame(
                    predicted_logic,
                    index=inputs.index,
                    columns=["kLUT", "kFF", "DSP"]
            )
            predicted_mem     = pd.DataFrame(
                    predicted_mem,
                    index=inputs.index,
                    columns=["BRAM", "URAM"]
            )
            predicted_resources = pd.concat([predicted_logic, predicted_mem], axis=1)

            if (feature == Features.bitblnd_cfg):
                data[t][Features.ESTIMATED_allresource_pct] = convert_resources_raw_to_pcts(predicted_resources)
            elif (feature == Features.passonly_bitblnd_cfg):
                data[t][Features.passonly_ESTIMATED_allresource_pct] = convert_resources_raw_to_pcts(predicted_resources)
            else:
                raise AssertionError("Unexpected control sequence")

    #print("\n\n\n TRAIN estimates:")
    #print(data['train'][Features.ESTIMATED_allresource_pct])
    #print("\n\n\n TEST estimates:")
    #print(data['test'][Features.ESTIMATED_allresource_pct])

    return data

























def train_bitstream_pass_and_frequency_estimators(data):

    """
        THIS is the "Bitstream-Completion Estimator Model", which estimates if the bitstream will be able to complete or not, for a given resource usage.
        It's basically a binary classifier on 5 inputs.
    """
    print("\n\n\n\n\n\n PREDICTING BITSTREAM COMPLETION NOW")
    NUM_ESTIMATORS_ARR = range(5,15)
    bitstream_error_dict = {}
    bitstream_models = {}
    for num_estimators in NUM_ESTIMATORS_ARR:
        print("--------------------------------------")
        print("num_estimators = {}".format(num_estimators))
        (bitstream_fin_model, Y_pred, Y_test) = train_and_test_model(
                data,
                Features.ESTIMATED_allresource_pct,
                Features.xclbinsuccess,
                num_estimators,
                forest_type=ForestType.CLASSIFIER,
                num_output_columns = 1,
                do_print = (num_estimators == NUM_ESTIMATORS_ARR[0])
            )

        badness_rating = 0
        true_positives = 0
        true_negatives = 0
        false_positives = 0
        false_negatives = 0
        for i in range(len(Y_pred)):
            rounded_prediction = (1 if (Y_pred[i] > 0.8) else 0)
            if (rounded_prediction != Y_test[i]):
                ### Grade false positives more harshly (we think it'll pass P&R but it actually fails)
                if (rounded_prediction == 1):
                    badness_rating += 3
                    false_positives += 1
                elif (rounded_prediction == 0):
                    badness_rating += 1
                    false_negatives += 1
                else:
                    raise AssertionError("the rounded prediction somehow wasn't 0 or 1...")

            elif (rounded_prediction == Y_test[i]):
                if (rounded_prediction == 0):
                    true_negatives += 1
                elif (rounded_prediction == 1):
                    true_positives += 1
                else:
                    raise AssertionError("the rounded prediction somehow wasn't 0 or 1...")

        fail_rate = badness_rating / len(Y_pred)

        print('BITSTREAM COMPLETION model: badness_rating :', badness_rating)
        print('BITSTREAM COMPLETION model: number of tests :', len(Y_pred))
        print('BITSTREAM COMPLETION model: false positives =', false_positives)
        print('BITSTREAM COMPLETION model: false negatives =', false_negatives)
        print('BITSTREAM COMPLETION model: true positives =', true_positives)
        print('BITSTREAM COMPLETION model: true negatives =', true_negatives)
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
    with open("models/bitstream_model.pkl", 'wb') as f:
        pickle.dump(BITSTREAM_PREDICTION_MODEL, f)


    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    """
        THIS is the "Frequency-prediction model", which estimates the frequency achieved, for a given resource usage.
        It's a 'normal' regression model, with 5 input variables and a continuous output variable.
    """
    print("\n\n\n\n\n\n PREDICTING FREQUENCIES NOW")


    NUM_ESTIMATORS_ARR = range(5,20)
    freq_mae_dict = {}
    frequency_models = {}
    for num_estimators in NUM_ESTIMATORS_ARR:
        print("--------------------------------------")
        print("num_estimators = {}".format(num_estimators))
        (freq_model, Y_pred, Y_test) = train_and_test_model(
                data,
                Features.passonly_ESTIMATED_allresource_pct,
                Features.passonly_frequency,
                num_estimators,
                forest_type=ForestType.REGRESSOR,
                num_output_columns = 1,
                do_print = (num_estimators == NUM_ESTIMATORS_ARR[0])
            )

        freq_mae = mean_absolute_error(Y_test, Y_pred)
        freq_max_abs_err = np.max( np.abs(Y_test - Y_pred) )
        freq_max_rel_err = np.max( np.abs(Y_pred/Y_test) )
        print('FREQUENCY model: Mean absolute Error:', freq_mae)
        print('FREQUENCY model: number of tests :', len(Y_pred))
        print('FREQUENCY model: MAX ABSOLUTE Error:', freq_max_abs_err)
        print('FREQUENCY model: MAX RELATIVE Error:', freq_max_rel_err)
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
    with open("models/frequency_model.pkl", 'wb') as f:
        pickle.dump(FREQUENCY_PREDICTION_MODEL, f)












def profile_training_and_testing():
    raise AssertionError("Uncomment the dataset you want to train with.")
    #data = read_training_data('./qor_data/FreqDataCSV_Feb14_2025.csv',
    #                            features=0,
    #                            test_fraction=TEST_SPLIT_FRACTION
    #)
    #data = read_training_data('./qor_data/FreqDataCSV_Feb27_2025.csv',
    #                            features=0,
    #                            test_fraction=TEST_SPLIT_FRACTION
    #)

    ##################################
    ### TRAINING THE RESOURCE-ESTIMATION MODELS
    ##################################
    train_resource_estimators(
        data
        ,num_output_columns = 5
    )
    print("----------------------------------")
    train_resource_estimators(
        data
        ,num_output_columns = 3
    )
    print("----------------------------------")
    train_resource_estimators(
        data
        ,num_output_columns = 2
    )

    data = generate_all_resource_estimates(data)

    for i in range(0, 5):
        print("----------------------------------")
    print("--- TRAINING BITSTREAM/FREQUENCY MODELS NOW")
    for i in range(0, 5):
        print("----------------------------------")
    ##################################
    ##################################
    train_bitstream_pass_and_frequency_estimators(data)























def test_models():
    """
    THIS FUNCTION is used, post-training, to test the behaviour of the models
    against some configs (e.g. those that might be selected during AutoDSE).
    """
    data = read_training_data('./qor_data/FreqDataCSV_Feb27_FOR_TESTING.csv',
                                features=0,
                                test_fraction=1.0
    )
    data = generate_all_resource_estimates(data)

    with open("models/bitstream_model.pkl", 'rb') as modelfile:
        bitstream_model = pickle.load(modelfile)
    with open("models/frequency_model.pkl", 'rb') as modelfile:
        frequency_model = pickle.load(modelfile)

    predictions = {}
    groundtruth = {}
    predictions['success']  = bitstream_model.predict(data['test'][Features.ESTIMATED_allresource_pct])
    predictions['freq']     = frequency_model.predict(data['test'][Features.passonly_ESTIMATED_allresource_pct])
    groundtruth['success']  = data['test'][Features.xclbinsuccess].to_numpy()
    groundtruth['freq']     = data['test'][Features.passonly_frequency].to_numpy()

    print("\n\n\nSUCCESS PREDICTIONS:")
    print(predictions['success'])
    print("\n\n\nFREQ PREDICTIONS:")
    print(predictions['freq'])
    print("\n\n\nSUCCESS GROUND TRUTH:")
    print(groundtruth['success'])
    print("\n\n\nFREQ GROUND TRUTH:")
    print(groundtruth['freq'])

    print("\n\n\nSUCCESS (predictions - ground truth):")
    print(predictions['success'] - groundtruth['success'])
    print("\n\n\nFREQ (predictions - ground truth):")
    print(predictions['freq'] - groundtruth['freq'])

    print("\n\n\n")

    ##################
    ### ANALYZING THE BITSTREAM MODEL PERFORMANCE
    ##################
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    for i in range(len(predictions['success'])):
        rounded_prediction = (1 if (predictions['success'][i] > 0.8) else 0)
        if (rounded_prediction != groundtruth['success'][i]):
            if (rounded_prediction == 1):
                false_positives += 1
            elif (rounded_prediction == 0):
                false_negatives += 1
            else:
                raise AssertionError("the rounded prediction somehow wasn't 0 or 1...")

        elif (rounded_prediction == groundtruth['success'][i]):
            if (rounded_prediction == 0):
                true_negatives += 1
            elif (rounded_prediction == 1):
                true_positives += 1
            else:
                raise AssertionError("the rounded prediction somehow wasn't 0 or 1...")

    print('BITSTREAM COMPLETION model: number of tests :', len(predictions['success']))
    print('BITSTREAM COMPLETION model: false positives =', false_positives)
    print('BITSTREAM COMPLETION model: false negatives =', false_negatives)
    print('BITSTREAM COMPLETION model: true positives =', true_positives)
    print('BITSTREAM COMPLETION model: true negatives =', true_negatives)


    ##################
    ### ANALYZING THE FREQUENCY MODLE PERFORMANCE
    ##################
    freq_mae = mean_absolute_error(groundtruth['freq'], predictions['freq'])
    freq_max_abs_err = np.max( np.abs(groundtruth['freq'] - predictions['freq']) )
    freq_max_rel_err = np.max( np.abs(predictions['freq'] / groundtruth['freq']) )
    print('FREQUENCY model: Mean absolute Error:', freq_mae)
    print('FREQUENCY model: number of tests :', len(predictions['freq']))
    print('FREQUENCY model: MAX ABSOLUTE Error:', freq_max_abs_err)
    print('FREQUENCY model: MAX RELATIVE Error:', freq_max_rel_err)












####################################################################


if __name__ == "__main__":

    #profile_training_and_testing()

    test_models()






