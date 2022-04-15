from flask import Flask, render_template
import pandas as pd
from flask import request
import numpy as np
import yfinance as yf
from tensorflow import keras
import time
from matplotlib.pyplot import title
import mplfinance as mpl
from datetime import datetime
import matplotlib.pyplot as plt
import os

PEOPLE_FOLDER = os.path.join('static')
model = keras.models.load_model('modelcon.h5')

def past_pred(m):
    df=m.iloc[-7:-1,:4]
    return df

def pre_pro(m , pm, df, data,step):
    if pm.iloc[len(m)-101:-1,:4].index[-1]<m.iloc[len(m)-101:-1,:4].index[-1]:
        pm =m.copy()
        
        mat = m.iloc[-101:-1,:4].to_numpy()/scaler
        mat = mat.reshape(-1, 100, 4)
        print('calculating 5 min')
        
        tem = pd.DataFrame(model.predict(mat)*scaler, columns=["Open", "High","Low","Close"])

        tem['time']= pm.index[-2] + pd.DateOffset(minutes=5)
        tem.set_index('time', drop=True, inplace=True)
        tem.index = pd.to_datetime(tem.index)
        
        df = df.append(tem)
        df.index = pd.to_datetime(df.index)
        
        m = yf.download(tickers=name, period=data, interval=step)
        
    else:
        print('No Change')
        m = yf.download(tickers=name, period=data, interval=step)
    return m , pm , df


    
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER



def create_chart():
    global m5 
    global pm5
    global df5
    global m15
    global pm15
    global df15
    global m30
    global pm30
    global df30
    global m60
    global pm60
    global df60
    global scaler
    global name
    m5 , pm5, df5 = pre_pro(m5 , pm5, df5, '5d', '5m')
    m15 , pm15, df15 = pre_pro(m15 , pm15, df15, '5d', '15m')
    m30 , pm30, df30 = pre_pro(m30 , pm30, df30, '60d', '30m')
    m60 , pm60, df60 = pre_pro(m60 , pm60, df60, '1y', '60m')
    print('showing charts')
    fig = mpl.figure(figsize=(20,20))
    ax1 = fig.add_subplot(4,2,1,style='yahoo')
    ax2 = fig.add_subplot(4,2,2,style='yahoo')
    ax3 = fig.add_subplot(4,2,3,style='yahoo')
    ax4 = fig.add_subplot(4,2,4,style='yahoo')
    ax5 = fig.add_subplot(4,2,5,style='yahoo')
    ax6 = fig.add_subplot(4,2,6,style='yahoo')
    ax7 = fig.add_subplot(4,2,7,style='yahoo')
    ax8 = fig.add_subplot(4,2,8,style='yahoo')

    df5.index = pd.to_datetime(df5.index, utc=True)
    df15.index = pd.to_datetime(df15.index, utc=True)
    df30.index = pd.to_datetime(df30.index, utc=True)
    df60.index = pd.to_datetime(df60.index, utc=True)


    mpl.plot(m5.iloc[len(m5)-6:,:4],type='candle',ax=ax1,axtitle='LIVE', mav =(3,6,9))
    mpl.plot(df5.iloc[-6:],type='candle',ax=ax2,axtitle='5 min', mav =(3,6,9))

    mpl.plot(m15.iloc[len(m15)-6:,:4],type='candle',ax=ax3,axtitle='LIVE', mav =(3,6,9))
    mpl.plot(df15.iloc[-6:],type='candle',ax=ax4,axtitle='15 min', mav =(3,6,9))

    mpl.plot(m30.iloc[len(m30)-6:,:4],type='candle',ax=ax5,axtitle='LIVE', mav =(3,6,9))
    mpl.plot(df30.iloc[-6:],type='candle',ax=ax6,axtitle='30 min', mav =(3,6,9))
    mpl.plot(m60.iloc[len(m60)-6:,:4],type='candle',ax=ax7,axtitle='LIVE', mav =(3,6,9))
    mpl.plot(df60.iloc[-6:],type='candle',ax=ax8,axtitle='60 min', mav =(3,6,9)) 

    plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], 'newfile.jpg'))
    print('file saved')
    return 'newfile.jpg'


    
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    global m5 
    global pm5
    global df5
    global m15
    global pm15
    global df15
    global m30
    global pm30
    global df30
    global m60
    global pm60
    global df60
    global scaler
    global name
    
    full_filename2 = os.path.join(app.config['UPLOAD_FOLDER'], 'newfile.jpg')
    
    if request.method == 'POST':
        name = request.form['nm']
        
        m5 = yf.download(tickers=name, period='5d', interval='5m')
        m15 = yf.download(tickers=name, period='5d', interval='15m')
        m60 = yf.download(tickers=name, period='1y', interval='60m')
        m30 = yf.download(tickers=name, period='60d', interval='30m')
        scaler = yf.download(tickers=name, period='60d', interval='90m').iloc[:,:4].to_numpy().max()*1.5
        tem = pd.DataFrame()
        pm5 = m5.iloc[:-1,:]
        pm15 = m15.iloc[:-1,:]
        pm60 = m60.iloc[:-1,:]
        pm30 = m30.iloc[:-1,:]
        
        df5 = past_pred(m5)
        df15 = past_pred(m15)
        df30 = past_pred(m30)
        df60 = past_pred(m60)
        
        file_name = create_chart()
          
        return render_template("result.html", user_image = full_filename2)
    else:
        file_name = create_chart()
        return render_template("result.html", user_image = full_filename2)

if __name__ == '__main__':
    app.run()