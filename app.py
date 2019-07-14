#Load the packages
from flask import Flask, render_template, request, redirect

import numpy as np
import pandas as pd

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import column, widgetbox
from bokeh.embed import components
from bokeh.models import ColumnDataSource

import requests
import simplejson as json

#Connect the app
app = Flask(__name__)

def get_dataset(stock):
    api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/' + stock + '.json'
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url)
    json1 = json.loads(raw_data.content)

    # convert json to pandas df
    date, open, close, adj_open, adj_close = [],[],[],[],[]
    # pdb.set_trace()
    for result in json1['data']:
        date.append(result[0])
        open.append(result[1])
        close.append(result[4])
        adj_open.append(result[8])
        adj_close.append(result[11])

    data = pd.DataFrame([date, open, close, adj_open, adj_close]).T
    data.columns = ["date", "open", "close", "adj_open", "adj_close"]

    cond = data['date'] > '2016-12-31'   # select only 2017-2018 data
    subset = data[cond]   # Select all cases where condition is met
    # pdb.set_trace()

    return subset

def datetime(x):
    return np.array(x, dtype=np.datetime64)

def update_plot(attr, old, new):
    new_subset = get_dataset(text_input.value)
    source.data = {'x': datetime(new_subset['date']), 'y': new_subset['adj_close']}

#Helper function
def get_plot(subset):
    p1 = figure(x_axis_type="datetime", title="Stock Closing Prices",
                width=600, height=600, tools='pan,box_zoom,reset,save')
    p1.grid.grid_line_alpha=0.3
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Price'

    source = ColumnDataSource(data={'x': datetime(subset['date']), 'y': subset['adj_close']})
    p1.line('x', 'y', color='#B2DF8A', legend='Closing Price', source=source)
    p1.legend.location = "top_left"

    return p1

@app.route('/', methods=['POST'])
def my_form_post():
    curr_ticker = request.form['text']    # input from user
    if curr_ticker == None:
        curr_ticker = "GOOG"
    processed_text = curr_ticker.upper()

    stock = processed_text  # set the default plot to GOOG
    subset = get_dataset(stock)

    #Setup plot
    p = get_plot(subset)
    script, div = components(p)

    #Render the page
    return render_template('graph.html', script=script, div=div, curr_ticker=curr_ticker)

@app.route('/')
def homepage():
    stock = 'GOOG'  # set the default plot to GOOG
    subset = get_dataset(stock)

    #Setup plot
    p = get_plot(subset)
    script, div = components(p)

    #Render the page
    return render_template('graph.html', script=script, div=div, curr_ticker="GOOG")

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # app.run()








#
# # Simple app.py that works!! :)
#
# from flask import Flask, render_template, request, redirect
#
# app = Flask(__name__)
#
# @app.route('/')
# def index():
#     return "OK!"
#   # return render_template('index.html')
#
# def hello_world():
#     return 'Hello World!'
#
# @app.route('/about')
# def about():
#   return render_template('about.html')
#
# if __name__ == '__main__':
#   app.run(port=33507)


 # To run: python3 app.py
 # Then type into browser: localhost:33507
