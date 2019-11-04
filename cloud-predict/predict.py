"""Google Cloud Online Prediction Requests
   Tests online prediction requests
   Use local credentials.json file for cloud auth with GOOGLE_APPLICATION_CREDENTIALS env
"""
import argparse
import pandas as pd
import googleapiclient.discovery
from instance_generator import CMLEPreProcessor


def get_instances(file, target_column):
    """Get instances from csv to predict
    Args:
        file: filename to get instances from csv
        target_column: response column to exclude for predictions
    Returns:
        tuple: original test data (pandas), instances to predict with response column removed (list vals)
    """
    data = pd.read_csv(file)
    instances = data.drop([target_column], axis=1)
    return data, instances.values.tolist()


def predict_json(project, model, instances, version=None):
    """Send json data to a deployed model for prediction.
    Args:
        project (str): project where the AI Platform Model is deployed.
        model (str): model name.
        instances ([[float]]): List of input instances, where each input
           instance is a list of floats.
        version: str, version of the model to target.
    Returns:
        Mapping[str: any]: dictionary of prediction results defined by the
            model.
    """
    # Create the AI Platform service object.
    # To authenticate set the environment variable
    # GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
    service = googleapiclient.discovery.build('ml', 'v1')
    name = 'projects/{}/models/{}'.format(project, model)
    if version is not None:
        name += '/versions/{}'.format(version)

    response = service.projects().predict(
        name=name,
        body={'instances': instances}
    ).execute()

    if 'error' in response:
        raise RuntimeError(response['error'])
    return response['predictions']


def predict_single(project, model, instance):
    """
    Predict single response
    Args:
        instance: string of values to predict response from
    Returns:
        Single output response float of probability
    """
    processed_instance = preprocessor.transform_string_instance(instance)
    pred = predict_json(project, model, [processed_instance])
    return pred


def predict_bulk(project, model, instances):
    """
    Predict multiple responses from a list of lists
    Args:
        instances: numpy list of lists containing values to predict
    Returns:
        list of responses, floating point probabilities
    """
    prediction_data = []
    for item in instances:
        # Blank between two commas stands for missing data.
        # Number stands for numerical data. Strings stand for categorical data.
        # Example record: 'NORTH,220.972,1.112453125,14055.71495,1.51,12,11,20,6,0.1,2000.182337,100000,2,70'
        transformed_instance = preprocessor.transform_list_instance(item)
        prediction_data.append(transformed_instance)
    preds = predict_json(project, model, prediction_data)
    return preds


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'project', help='Enter the Google project name')
    parser.add_argument(
        'model', help='Enter the model name')
    parser.add_argument(
        'file', help='Enter a test csv file with test data for predictions')
    parser.add_argument(
        'output_file', help='Enter output file name'
    )
    parser.add_argument(
        'target', help='Enter the response column name')
    args = parser.parse_args()

    preprocessor = CMLEPreProcessor()
    test_df, instances = get_instances(args.file, args.target)

    predictions = predict_bulk(args.project, args.model, instances)
    test_df['prediction'] = predictions
    test_df.to_csv(args.output_file, index=False)
