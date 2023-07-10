from flask import Flask, request, jsonify
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Extract the stock symbol from the request data
    stock = data['stock']
    
    # Calculate the date 5 years ago
    start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')

    # Download historical market data
    data = yf.download(stock, start=start_date, end=datetime.now().strftime('%Y-%m-%d'))

    # Calculate features
    data['SMA'] = data['Close'].rolling(window=14).mean()
    data['EMA'] = data['Close'].ewm(span=14, adjust=False).mean()

    # Drop missing values
    data = data.dropna()

    # Create a target variable
    data.loc[:, 'Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)

    # Split the data into features and target
    X = data[['SMA', 'EMA']]
    y = data['Target']

    # Train a model
    model = RandomForestClassifier()
    model.fit(X[:-1], y[:-1])

    # Predict whether the stock price will increase tomorrow
    prediction = model.predict(X[-1:])
    prediction_text = 'Buy' if prediction else 'Wait'

    # Prepare the response
    response = {
        'stock': stock,
        'prediction': prediction_text
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
