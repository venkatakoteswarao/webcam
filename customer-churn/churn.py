import numpy as np
import pandas as pd
import pickle, logging
from rich.logging import RichHandler
from flask import Flask, request, jsonify

# Logging setup
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger("rich")

# Load data and models
df = pd.read_csv('data/preprocessed_data.csv')
scaler = pickle.load(open('data/ML_models/StandardScaler.pkl', 'rb'))
InternetServiceEncoder = pickle.load(open('data/ML_models/InternetServiceEncoder.pkl', 'rb'))
OnlineSecurityEncoder = pickle.load(open('data/ML_models/OnlineSecurityEncoder.pkl', 'rb'))
ContractEncoder = pickle.load(open('data/ML_models/ContractEncoder.pkl', 'rb'))
StreamingTVEncoder = pickle.load(open('data/ML_models/StreamingTVEncoder.pkl', 'rb'))
DependentsEncoder = pickle.load(open('data/ML_models/DependentsEncoder.pkl', 'rb'))
model = pickle.load(open('data/ML_models/stackedModel.pkl', 'rb'))

app = Flask(__name__)

# Endpoint to provide dropdown options to Spring Boot
@app.route('/options', methods=['GET'])
def get_options():
    return jsonify({
        "DependentsList": sorted(df.Dependents.unique().tolist()),
        "InternetServiceList": sorted(df.InternetService.unique().tolist()),
        "OnlineSecurityList": sorted(df.OnlineSecurity.unique().tolist()),
        "ContractList": sorted(df.Contract.unique().tolist()),
        "StreamingTVList": sorted(df.StreamingTV.unique().tolist())
    })

# Predict endpoint aligned with Spring Boot controller
@app.route('/predict', methods=['POST'])
def predict():
    data = request.form  # Spring Boot sends POST form data

    Dependents = data.get('Dependents')
    InternetService = data.get('InternetService')
    OnlineSecurity = data.get('OnlineSecurity')
    Contract = data.get('Contract')
    StreamingTV = data.get('StreamingTV')
    MonthlyCharges = float(data.get('MonthlyCharges', 0))

    # Encode categorical variables
    DependentsEncoded = DependentsEncoder.transform([Dependents])[0]
    InternetServiceEncoded = InternetServiceEncoder.transform([InternetService])[0]
    OnlineSecurityEncoded = OnlineSecurityEncoder.transform([OnlineSecurity])[0]
    ContractEncoded = ContractEncoder.transform([Contract])[0]
    StreamingTVEncoded = StreamingTVEncoder.transform([StreamingTV])[0]

    logging.info('Encoding done')

    # Prepare input for model
    to_predict = scaler.transform([[
        DependentsEncoded, InternetServiceEncoded, OnlineSecurityEncoded,
        ContractEncoded, StreamingTVEncoded, MonthlyCharges
    ]])

    prediction = model.predict(to_predict)[0]

    if prediction == 1:
        churn_message = "Customer is likely to churn"
    else:
        churn_message = "Customer is unlikely to churn"

# Return prediction as JSON
    return jsonify({"prediction": churn_message})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
