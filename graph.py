#!/usr/bin/env python
# coding: utf-8

# In[33]:


import datetime
from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.graph_objects import Layout
from plotly.graph_objs import Scatter, Figure, Layout
import plotly.io as pio
import numpy as np
import pandas as pd

population_202104 = 23514196
csv_filename = '~/Programs/VaccineCOVID19Taiwan/VaccineCOVID19Taiwan - public.csv'
Date = '日期'
Event = '事件'
InjectedAmount = '累計施打'
InjectedAmountCorrect = '校正累計施打'
ConfirmedLocalDaily = '單日本土確診'
DeathDaily = '單日死亡'
FinalCorrectAmount = '完成本土增補'

title = '臺灣COVID-19疫苗接種統計報表'
label_taiwan_vac = '疫苗接種(劑/人口)'
label_bottom = '事件/統計日期(西元)'
label_right = '新增本土確診/死亡（人）'
label_left = '疫苗接種(%)'
label_confirmed = '新增本土確診(人)'
label_correction = '累計校正回歸(人)'
label_death = '新增死亡(人)'

first_date = datetime.datetime.fromisoformat('2021-03-01')
last_date = datetime.datetime.today() + datetime.timedelta(days=1)
last_date = datetime.datetime.fromisoformat('2021-07-21')
dpi = 200


# In[37]:


def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def verticalizeText(text):
    text = text.strip()
    text_v = ''        
    isE = [isEnglish(t) for t in text]
    for j in range(len(text)):
        if text[j] == ' ':
            continue
        if j < len(text)-1:
            if text[j] == '/':
                enter = True
            elif j < len(text)-2:
                if text[j+1] == '/':
                    enter = True
                elif text[j+1] == '#':
                    enter = True
                elif isE[j] and isE[j+1]:
                    enter = False
                elif isE[j] and not isE[j+1]:
                    enter = True
                elif not isE[j] and isE[j+1]:
                    enter = True
                elif not isE[j] and not isE[j+1]:
                    enter = True
            elif isE[j] and isE[j+1]:
                enter = False
            elif isE[j] and not isE[j+1]:
                enter = True
            elif not isE[j] and isE[j+1]:
                enter = True
            elif not isE[j] and not isE[j+1]:
                enter = True
        else:
            enter = False

        if enter:
            text_v += text[j] + '\n'
        else: 
            text_v += text[j]
    
    return text_v


# In[38]:


df = pd.read_csv(csv_filename)
df = df[~df[Date].isnull()]
df.loc[:,Date] = df[Date].astype('datetime64[ns]')
df.set_index(Date,inplace=True)
ind = (df.index >= first_date + datetime.timedelta(days=-1)) * (df.index <= last_date.strftime('%Y-%m-%d'))
df = df[ind]
df.loc[(last_date+datetime.timedelta(days=-1)).strftime('%Y-%m-%d'),InjectedAmountCorrect] =     df.loc[(last_date+datetime.timedelta(days=-1)).strftime('%Y-%m-%d'),InjectedAmount]

ind = df[InjectedAmountCorrect].isnull()
df.loc[ind,InjectedAmountCorrect] = df.loc[ind,InjectedAmount]
df['mavg'] = df[InjectedAmountCorrect].interpolate()


# In[86]:


vaccine_color = '#6F00D2'
event_color = '#000000'
plot_bgcolor = '#FFFFFF'
# Create traces
#fig = go.Figure(shared_xaxes=True,specs=[[{"secondary_y": True}]])
#fig = make_subplots(rows=1, cols=1, shared_xaxes=True,specs=[[{"secondary_y": True}]])
fig = make_subplots(shared_xaxes=True,specs=[[{"secondary_y": True}]])

hovertemplate = '%{y:.2f}%<extra></extra>'
ind = (~df[InjectedAmountCorrect].isnull()) & (df.index < (last_date + datetime.timedelta(days=-1)))
ind = ind & ~(df[InjectedAmountCorrect]==0)
x = df.index[ind]
y = df[InjectedAmountCorrect][ind]/population_202104*100
# data[0]
fig.add_trace(
    go.Scatter(
        x=x, 
        y=y,
        name=label_taiwan_vac,
        mode='lines',
        line=dict(color=vaccine_color, width=2, dash='dash'),
        hovertemplate=hovertemplate,
    ), secondary_y=True)
fig.update_layout(hovermode="x",hoverdistance=100)
#fig.update_layout(hovermode="x unified")
#fig.update_layout(hovermode='closest')

ind = (~df['累計第一劑_合計'].isnull())# & (df.index > datetime.datetime.fromisoformat('2021-06-20') )
ind = ind & (df.index < (last_date + datetime.timedelta(days=-1)) )
dd = df.index[ind]
aa2 = df['累計第二劑_合計'][ind]/population_202104*100
# data[1]
fig.add_trace(
    go.Scatter(
        x=dd, 
        y=aa2,
        name='第二劑接種(%)',
        mode='lines',
        line=dict(color='blue', width=1.5, dash='dot'),
        hovertemplate=hovertemplate,
    ), secondary_y=True)
# data[2]
fig.add_trace(
    go.Scatter(
        x=[dd[0],dd[-1]],
        y=[aa2[0],aa2[-1]],
        mode='markers',
        marker={"size": 5, "color":'blue'},
        showlegend=False,
        hoverinfo='none',
    ), secondary_y=True)

#ax.plot(dd[0],aa2[0],'o',color='blue')
#ax.plot(dd[-1],aa2[-1],'o',color='blue')

###### Show Event #####
#hovertemplate = '%{x}<br>%{text}<extra></extra>'
hovertemplate = '%{text}<extra></extra>'
ind = ~df[Event].isnull() & (df.index < (last_date + datetime.timedelta(days=-1)))
x = df.index[ind]
y = df.loc[ind,"mavg"]/population_202104*100
label = df.loc[ind,Event]
eventURL = df.loc[ind,'事件參考1']
ind = eventURL.isnull()
for i in eventURL.index[ind]:
    text = label[i].replace(' / ','+')
    if '#' in text:
        text = text.replace('#','')
        text = ''.join([i for i in text if not i.isdigit()])
    text += ' {:%B %d, %Y}'.format(i)
    if not '#' in text:
        eventURL[i] = 'https://www.google.com/search?q="' +text+ '"'#'https://www.google.com'
    else:
        eventURL[i] = 'https://www.google.com/search?q="' +text+ '"'

label = label.to_numpy()
eventURL = eventURL.to_numpy()
# data[3]
fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        name=Event,
        mode='markers',
        text=label,
        customdata=eventURL,
        marker={"size": 5, "color":event_color},
        showlegend=False,
        hovertemplate=hovertemplate,
    ), secondary_y=True)


##### Comfirmed #####
barwidth = 86400 * 800
#hovertemplate = 'Date=%{x}<br>Diff=%{y}<extra></extra>'
hovertemplate = '%{text:d}人<extra></extra>'

ind = ~ (df[DeathDaily] == 0) & ~ df[DeathDaily].isnull()
death_color = 'red'
# data[4]
fig.add_trace(
    go.Bar(
        x=df.index[ind],y=df[DeathDaily][ind],
        width=barwidth,
        name=label_death,
        text=df[DeathDaily][ind].astype(int),
        marker_color=death_color,            
        hovertemplate=hovertemplate,
        texttemplate=' ',
    ), secondary_y=False)

ind = ~ (df[ConfirmedLocalDaily] == 0)  & ~ df[ConfirmedLocalDaily].isnull()
confirmd_color = '#FFAD86'
fig.add_trace(
    go.Bar(
        x=df.index[ind],y=(df[ConfirmedLocalDaily]-df[DeathDaily])[ind],
        width=barwidth,
        name=label_confirmed,
        text=df[ConfirmedLocalDaily][ind].astype(int),
        marker_color=confirmd_color,
        hovertemplate=hovertemplate,
        texttemplate=' ',
    ), secondary_y=False)

ind = ~ (df[FinalCorrectAmount] == 0 ) & ~ df[FinalCorrectAmount].isnull()
correction_color = 'gold'
fig.add_trace(
    go.Bar(
        x=df.index[ind],y=df[FinalCorrectAmount][ind],
        width=barwidth,
        name=label_correction,
        text=df[FinalCorrectAmount][ind].astype(int),
        marker_color=correction_color,
        hovertemplate=hovertemplate,
        texttemplate=' ',
    ), secondary_y=False)

fig.update_layout(barmode='stack')


alpha_level1 = 0.2
color_level1 = 'lightgreen'
alpha_level2 = 0.2
color_level2 = 'gold'
alpha_level3 = 0.2
color_level3 = 'orange'
alpha_alert = 1
color_alert = '#FFD2D2'
alpha_vaccine = 1
color_vaccine = '#D2E9FF'


fig.add_vrect(
    x0='2021-03-01', x1='2021-05-11',
    fillcolor=color_level1, opacity=alpha_level1,
    layer="below", line_width=0,
    name='first'
)
fig.add_vrect(
    x0="2021-05-11", x1="2021-05-19",
    fillcolor=color_level2, opacity=alpha_level2,
    layer="below", line_width=0,
)
fig.add_vrect(
    x0="2021-05-19", x1=last_date,
    fillcolor=color_level3, opacity=alpha_level3,
    layer="below", line_width=0,
)

# infected dates
dates_infected = ['2021-04-22','2021-04-29','2021-05-11','2021-05-12','2021-05-23',
                  '2021-06-01','2021-06-23','2021-07-02','2021-07-13']
dates_vaccine = ['2021-06-10','2021-07-19']

# vaccine events
ind = ~df[Event].isnull() & (df.index < (last_date + datetime.timedelta(days=-1)))
for i in df[ind].index:
    if '抵臺' in df.loc[i,Event]:
        date0 = i - datetime.timedelta(hours=12)
        date1 = i + datetime.timedelta(hours=12)
        fig.add_vrect(
            x0=date0, x1=date1,
            fillcolor=color_vaccine, opacity=alpha_vaccine,
            layer="below", line_width=0,
        )

for d in dates_vaccine:
    date0 = datetime.datetime.fromisoformat(d) - datetime.timedelta(hours=12)
    date1 = datetime.datetime.fromisoformat(d) + datetime.timedelta(hours=12)
    fig.add_vrect(
        x0=date0, x1=date1,
        fillcolor=color_vaccine, opacity=alpha_vaccine,
        layer="below", line_width=0,
    )

# infected events
for d in dates_infected:
    date0 = datetime.datetime.fromisoformat(d) - datetime.timedelta(hours=12)
    date1 = datetime.datetime.fromisoformat(d) + datetime.timedelta(hours=12)
    fig.add_vrect(
        x0=date0, x1=date1,
        fillcolor=color_alert, opacity=alpha_alert,
        layer="below", line_width=0,
    )


fig.update_layout(
    plot_bgcolor=plot_bgcolor,
    title={'text': title,'x':0.5,'xanchor': 'center'},
    margin_l=0,
    margin_r=0,
    margin_t=50,
    margin_b=0,
    autosize=True)


##### legend #####
fig.update_layout(
    legend_title="臺灣人口基數",
    legend=dict(
        traceorder='normal',
        yanchor="top",
        y=0.98,
        xanchor="left",
        x=0.01,
        bordercolor="darkgray",
        borderwidth=1,
))

# Primary yaxis
fig.update_yaxes(
    title_text=label_right,
    range=(0,600),
    secondary_y=False,
    color=death_color,
    showline=True,
    linecolor=death_color,
    ticks="outside",
    showgrid=True,
    gridcolor='darkgray',

)

# Secondary yaxis
fig.update_yaxes(
    title_text=label_left,
    range=(0,100), 
    secondary_y=True,
    color=vaccine_color,
    showgrid=False,
    showline=True,
    linecolor=vaccine_color,
    ticks="outside"
)

# 
fig.update_xaxes(
    title_text=label_bottom,
    range=('2021-03-01',last_date),
    constrain='domain',
    showline=True,
    linecolor='black',
    mirror=True,
    ticks="outside",
)

#fig.update_layout(dragmode='drawrect',
                  # style of new shapes
#                  newshape=dict(
#                      fillcolor='blue',
#                      line=dict(color='black', width=2, dash='dash'),
#                      opacity=0.5))

##### function #####


#scatter.on_click(update_point)




fig.update_layout(height=900)#,width=800)
fig.show()
#fig.show(config={'modeBarButtonsToAdd':['drawline',
#                                        'drawopenpath',
#                                        'drawclosedpath',
#                                        'drawcircle',
#                                        'drawrect',
#                                        'eraseshape'
#                                       ]})
#fig.update_layout(height=900,width=1600)
#pio.write_html(fig, file='_includes/figure.html', auto_open=False)


# In[87]:


# convert to .py
get_ipython().system('jupyter nbconvert --to script graph.ipynb')


# In[88]:


# https://github.com/plotly/plotly.py/issues/1756

from plotly.offline import plot
import pandas as pd
import plotly.graph_objs as go
import re

# mapbox_access_token = '...'

# Build scattermapbox trace and store URL's in the customdata
# property. The values of this list will be easy to get to in the
# JavaScript callback below
data = [
    go.Scatter(
        x=[1, 2, 3],
        y=[1, 3, 2],
        mode='markers',
        marker=dict(
            size=14
        ),
        name='mapbox 1',
        text=['Montreal'],
        customdata=['https://www.baidu.com', 'http://www.fabricschina.com.cn/', 'https://www.zhihu.com']
    )
]

# Build layout
layout = go.Layout(
    hovermode='closest',
)

# Build Figure
#fig = go.Figure(
#    data=data,
#    layout=layout,
#)

# Get HTML representation of plotly.js and this figure
plot_div = plot(fig, output_type='div', include_plotlyjs=True)

# Get id of html div element that looks like
# <div id="301d22ab-bfba-4621-8f5d-dc4fd855bb33" ... >
res = re.search('<div id="([^"]*)"', plot_div)
div_id = res.groups()[0]

# Build JavaScript callback for handling clicks
# and opening the URL in the trace's customdata 
js_callback = """
<script>
var plot_element = document.getElementById("{div_id}");
plot_element.on('plotly_click', function(data){{
    console.log(data);
    var point = data.points[0];
    if (point) {{
        console.log(point.customdata);
        if (point.customdata){{
            window.open(point.customdata);
        }}
    }}
}})
</script>
""".format(div_id=div_id)

# Build HTML string
html_str = """
<html>
<body>
{plot_div}
{js_callback}
</body>
</html>
""".format(plot_div=plot_div, js_callback=js_callback)


# Write out HTML file
with open('_includes/figure.html', 'w') as f:
    f.write(html_str)


# In[89]:


eventURL


# In[ ]:




