"""
Main module for traffic analysis, predictions, API
"""
import argparse
#import pkg_resources

# Predictions based on geographic points x, y?
# Aggregate counts for roads?
# Heatmap for geo coords?

def main():
    """
    Main argparse for command line predictions
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('model', 
        help='Enter the model type to train, random forest, XGBoost, Logistic Regression', 
        choices=['rf', 'xgb', 'lr']
        )
    args = parser.parse_args()
    print(args.model)
    #train_model(args.model)
    
if __name__ == '__main__':
    main()