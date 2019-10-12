"""Google Cloud Online Prediction Requests
   Tests online prediction requests
   Use local credentials.json file for cloud auth
"""
import argparse
import json
import googleapiclient.discovery
from instance_generator import CMLEPreProcessor


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


if __name__ == '__main__':
    # Blank between two commas stands for missing data.
    # Number stands for numerical data. Strings stand for categorical data.
    # Example record: 'NORTH,220.972,1.112453125,14055.71495,1.51,12,11,20,6,0.1,2000.182337,100000,2,70'
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'project', help='Enter the Google project name')
    parser.add_argument(
        'model', help='Enter the training datasize for the model')
    parser.add_argument(
        'instance', help='Enter a single instance to predict in string format comma separated')
    args = parser.parse_args()
    preprocessor = CMLEPreProcessor()
    processed_data = preprocessor.transform_string_instance(args.instance)
    preds = predict_json(args.project, args.model, [processed_data])
    print(preds)
