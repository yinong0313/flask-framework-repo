from flask import Flask, render_template, request, session, redirect, url_for, session
from flask_wtf import FlaskForm
import requests
import json
import io
from io import BytesIO
from flask import send_file
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
#from StringIO import StringIO
from wtforms import (StringField, BooleanField, DateTimeField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField)
from wtforms.validators import DataRequired


app = Flask(__name__)

# Configure a secret SECRET_KEY
app.config['SECRET_KEY'] = 'mysecretkey'


class InfoForm(FlaskForm):
    #User defined sticker and date
    sticker = StringField('Please type a stock sticker',validators=[DataRequired()],render_kw={"placeholder": "NOVA"})
    year = RadioField('Please choose a year', choices=[('2018','2018'),('2017','2017'),('2016','2016')])
    month = StringField('Please enter a month',render_kw={"placeholder": "3"})
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():

    # Create instance of the form.
    form = InfoForm()

    # If the form is valid on submission
    if form.validate_on_submit():
        # Grab the data from the breed on the form.
        session['sticker'] = form.sticker.data
        session['year'] = form.year.data
        session['month'] = form.month.data

        #Month adjust
        if session['month'] == '2':
            date_url = 'start_date='+ session['year']+ '-' + session['month'] + '-' + '1' +'&end_date='+ session['year']+ '-' + session['month'] + '-' + '28'
        elif session['month'] in ['4','6','9','11']:

            date_url = 'start_date='+ session['year']+ '-' + session['month'] + '-' + '1' +'&end_date='+ session['year']+ '-' + session['month'] + '-' + '30'
        else:
            date_url = 'start_date='+ session['year']+ '-' + session['month'] + '-' + '1' +'&end_date='+ session['year']+ '-' + session['month'] + '-' + '31'

        #request data (json data)
        r = requests.get('https://www.quandl.com/api/v3/datasets/XETR/'+ session['sticker'] + '.json?' + date_url + '&api_key=6f1D__GLb6MaCsgt8Peo')
        json_object =r.json()
        close_price=[]
        date_time = []
        date_range = range(len(json_object['dataset']['data']))
        for num in date_range:
            close_price.append(json_object['dataset']['data'][num][4])
            date_time.append(json_object['dataset']['data'][num][0])

        #start plotting
        plt.clf()
        plt.cla()
        plt.close()
        month_dic = {'1':'Jan.','2':'Feb.','3':'Mar.','4':'Apr.','5':'May','6':"Jun.",
                        '7':'Jly.','8':'Aug.','9':'Sep.','10':'Oct.','11':'Nov.','12':'Dec.'}


        #figure settings
        tick_spacing = 4
        fig, ax = plt.subplots(1,1)
        ax.plot(date_time[::-1],close_price[::-1])
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        plt.title('Here is the price for stock {} within {} {}:'.format(session['sticker'],month_dic[session['month']],session['year']))
        plt.xlabel('Date')
        plt.ylabel('Close Price ($)')
        plt.xticks(rotation=30,fontsize='5')
        plt.yticks(fontsize='6')

        #save plot
        fig = plt.gcf()
        fig.set_size_inches(7,5)
        buffer = io.BytesIO()
        fig.canvas.print_png(buffer)
        buffer.seek(0)

        return send_file(buffer, mimetype="image/png")

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
