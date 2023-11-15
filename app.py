from flask import Flask, request, render_template
import pandas as pd
import numpy as np

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    if file:
        try:
            dataset = pd.read_csv(file)

            dataset['payment_RUB'] = dataset['payment_RUB'].str.replace(',', '.', regex=True).astype(float)

            dataset['created_at.2'] = pd.to_datetime(dataset['created_at.2'])

            dataset['first_order_date'] = dataset.groupby('emailclient')['created_at.2'].transform('min').dt.strftime(
                '%m.%Y')

            grouped = dataset.groupby('emailclient')
            dataset['days_since_first_order'] = grouped['created_at.2'].transform(lambda x: (x - x.min()).dt.days)

            dataset['days30_since_first_order'] = np.ceil(dataset['days_since_first_order'] / 30) * 30

            dataset2 = dataset.groupby(['emailclient', 'first_order_date', 'days30_since_first_order', ])[
                'payment_RUB'].sum().reset_index()

            from pandas.core.tools.datetimes import to_datetime
            dataset2 = dataset2.sort_values(by=['emailclient', 'days30_since_first_order'])
            dataset2['cumulative_payment_RUB'] = dataset2.groupby('emailclient')['payment_RUB'].cumsum()

            return render_template('results.html', data=dataset2)
        except Exception as e:
            return f"Произошла ошибка при обработке файла: {str(e)}"
    else:
        return "Файл не загружен."


if __name__ == '__main__':
    app.run(debug=True)
