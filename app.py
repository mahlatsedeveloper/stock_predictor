from flask import Flask, render_template, request
import yfinance as yf
from matplotlib.figure import Figure
from sklearn.ensemble import RandomForestClassifier
import io
import base64
import urllib
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock = request.form.get('stock')

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

        # Plot closing price, SMA, and EMA
        fig = Figure(figsize=(14, 7))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(data.index, data['Close'], label='Closing Price', color='blue')
        ax.plot(data.index, data['SMA'], label='14-day SMA', color='red')
        ax.plot(data.index, data['EMA'], label='14-day EMA', color='green')
        ax.set_title(f'{stock} Closing Price, 14-day SMA, and 14-day EMA')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()
        ax.grid(True)
        img = io.BytesIO()
        fig.savefig(img, format='png')
        img.seek(0)
        plot_url = urllib.parse.quote(base64.b64encode(img.read()).decode())

        return render_template('index.html', prediction_text=prediction_text, plot_url=plot_url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
