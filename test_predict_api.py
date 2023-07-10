import unittest
from flask import Flask, jsonify
from flask.testing import FlaskClient

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    # Your prediction logic here
    prediction_result = "Buy"  # Placeholder for the prediction result

    response = {
        'stock': 'AAPL',
        'prediction': prediction_result
    }

    return jsonify(response)

class FlaskAPITestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_predict_endpoint(self):
        data = {
            'stock': 'AAPL'
        }

        response = self.app.post('/predict', json=data)
        json_data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data['stock'], 'AAPL')
        self.assertEqual(json_data['prediction'], 'Buy')

if __name__ == '__main__':
    unittest.main()
