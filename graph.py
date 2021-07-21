#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[172]:


import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
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
label_bottom = '事件/統計日期(西元)'
label_right = '新增本土確診/死亡（人）'
label_left = '疫苗接種(%)'

first_date = datetime.datetime.fromisoformat('2021-03-01')
last_date = datetime.datetime.today() + datetime.timedelta(days=1)
dpi = 200


# In[173]:


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


# In[174]:



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


# In[179]:


vaccine_color = '#6F00D2'
event_color = '#000000'
# Create traces
#fig = go.Figure()
#fig = make_subplots(rows=1, cols=1, shared_xaxes=True,specs=[[{"secondary_y": True}]])
fig = make_subplots(shared_xaxes=True,specs=[[{"secondary_y": True}]])

hovertemplate = '%{y:.2f}%<extra></extra>'
ind = (~df[InjectedAmountCorrect].isnull()) & (df.index < (last_date + datetime.timedelta(days=-1)))
ind = ind & ~(df[InjectedAmountCorrect]==0)
x = df.index[ind]
y = df[InjectedAmountCorrect][ind]/population_202104*100
fig.add_trace(
    go.Scatter(
        x=x, 
        y=y,
        name=InjectedAmountCorrect,
        mode='lines',
        line=dict(color=vaccine_color, width=2, dash='dot'),
        hovertemplate=hovertemplate,
    ), secondary_y=True)
fig.update_layout(hovermode="x")
#fig.update_layout(hovermode="x unified")

#hovertemplate = '%{x}<br>%{text}<extra></extra>'
hovertemplate = '%{text}<extra></extra>'
ind = ~df[Event].isnull() & (df.index < (last_date + datetime.timedelta(days=-1)))
x = df.index[ind]
y = df.loc[ind,"mavg"]/population_202104*100
label = df.loc[ind,Event].to_numpy()
fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        name=Event,
        mode='markers',
        text=label,
        marker={"size": 5, "color":event_color},
        hovertemplate=hovertemplate,
    ), secondary_y=True)

#hovertemplate = 'Date=%{x}<br>Diff=%{y}<extra></extra>'
hovertemplate = '%{text}人<extra></extra>'

ind = ~ (df[DeathDaily] == 0)
death_color = 'red'
fig.add_trace(
    go.Bar(
        x=df.index[ind],y=df[DeathDaily][ind],
        name=DeathDaily,
        text=df[DeathDaily][ind],
        marker_color=death_color,            
        hovertemplate=hovertemplate,
    ), secondary_y=False)

ind = ~ (df[ConfirmedLocalDaily] == 0)
confirmd_color = '#FFAD86'
fig.add_trace(
    go.Bar(
        x=df.index[ind],y=(df[ConfirmedLocalDaily]-df[DeathDaily])[ind],
        name=ConfirmedLocalDaily,
        text=df[ConfirmedLocalDaily][ind],
        marker_color=confirmd_color,
        hovertemplate=hovertemplate,
    ), secondary_y=False)

ind = ~ (df[FinalCorrectAmount] == 0)
correction_color = 'gold'
fig.add_trace(
    go.Bar(
        x=df.index[ind],y=df[FinalCorrectAmount][ind],
        name=FinalCorrectAmount[2:],
        text=df[FinalCorrectAmount][ind],
        marker_color=correction_color,
        hovertemplate=hovertemplate,
    ), secondary_y=False)

fig.update_layout(barmode='stack')

fig.update_layout(
    width=1200, height=675,
    title={'text': title,'x':0.5,'xanchor': 'center'},
    xaxis_title=label_bottom,
#    yaxis_title=label_right,
    legend_title="Legend Title",)

fig.update_yaxes(title_text=label_right,range=(0,600), secondary_y=False)
fig.update_yaxes(title_text=label_left,
                 range=(0,30), 
                 secondary_y=True,
                 color=vaccine_color,
#                 font=dict(
#                    family="Courier New, monospace",
#                    size=18,
#                    color=vaccine_color
                 )#,)

alpha_level1 = 1
color_level1 = 'lightgreen'
alpha_level2 = 1
color_level2 = 'gold'
alpha_level3 = 1
color_level3 = 'orange'
alpha_alert = 1
color_alert = '#FFD2D2'
alpha_vaccine = 1
color_vaccine = '#D2E9FF'

fig.add_vline(x="2015-05-11", line_width=3, line_dash="dash", line_color="green")
# Add shape regions
fig.add_vrect(
    x0="2021-03-01", x1="2015-05-11",
   fillcolor=color_level1, opacity=alpha_level1,
    layer="below", line_width=0,
)
#fig.add_vrect(
#    x0="2021-05-11", x1="2015-05-19",
#    fillcolor=color_level2, opacity=alpha_level2,
#    layer="below", line_width=0,
#),
#fig.add_vrect(
#    x0="2021-05-19", x1="2021-07-20",
#    fillcolor=color_level3, opacity=alpha_level3,
#    layer="below", line_width=0,
#),


#fig.update_layout(
#    title="Plot Title",
#    xaxis_title="X Axis Title",
#    yaxis_title="Y Axis Title",
#    legend_title="Legend Title",
#    font=dict(
#        family="Courier New, monospace",
#        size=18,
#        color="RebeccaPurple"
#    )

fig.update_xaxes(
    range=('2021-03-01','2021-07-20'),
    constrain='domain'
)


fig.show()
fig.update_layout(width=1600, height=900)
pio.write_html(fig, file='_includes/figure.html', auto_open=False)


# In[ ]:




