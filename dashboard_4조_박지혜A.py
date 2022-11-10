# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 09:04:55 2022

@author: PC
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

data = pd.read_csv("서울주문정보사본2.csv", encoding = 'utf-8')
data["주문일시"] = pd.to_datetime(data["주문일시"], format="%Y-%m-%d")
data.sort_values("주문일시", inplace = True)

app = dash.Dash(__name__)
#title when you search
app.title= "주문수량 분석"

app.layout = html.Div(
        #header 
    children=[
        html.Div(
            children=[
                html.P(
                    children= "😀", className="header_emoji",                   
                    ),
                html.H1(
                    children="xxx 온라인 쇼핑몰 대시보드",
                    #style={"fontSize": "48px","color": "green"}
                    className="header_title",
                    ),
                html.P(
                    children="4조 - 판매가 주문수량 비교 분석", className="header_description",),
                    ],
                    className ='header',                    
                ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="행정구", className="menu-title"),
                        dcc.Dropdown(
                            id="region",
                            options=[
                                {"label": gu, "value": gu}
                                for gu in np.sort(data.gu.unique())
                            ],
                            value= '영등포구',
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="카테고리명", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {"label": 카테고리명, "value": 카테고리명}
                                for 카테고리명 in data.카테고리명.unique()
                            ],
                            value= "홈데코레이션",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="주문기간",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.주문일시.min().date(),
                            max_date_allowed=data.주문일시.max().date(),
														initial_visible_month=data.주문일시.min().date(),
                            start_date=data.주문일시.min().date(),
                            end_date=data.주문일시.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
            ),
        html.Div(
                children=[
                    html.Div(
                        children=dcc.Graph(
                            id="price",
                            config={"displayModeBar": False},
                            figure={
                                "data" : [
                                    {
                                        "x": data["주문일시"],
                                        "y": data["판매가"],
                                        "type": "line",
                                        "hovertemplate": "%{y:.2f}₩"
                                        "<extra></extra>",
                                        },
                                    ],
                                "layout": {
                                    "title": {
                                        "text": "판매액",
                                        "x": 2,
                                        "xanchor": "center",
                                        },
                                    "xaxis": {"fixedrange": True},
                                    "yaxis": {
                                        "tickprefix": "₩",
                                        "fixedrange" :True,
                                        },
                                        "colorway": ["#17B897"],
                                    },
                                },
                            ),
                            className="card",
                        ),
                        html.Div(
                            children=dcc.Graph(
                                id="order",
                                config={"displayModeBar": False},
                                figure={
                                    "data": [
                                        {
                                            "x": data["주문일시"],
                                            "y": data["수량"],
                                            "type": "bar",
                                        },
                                    ],
                                    "layout": {
                                        "title": {
                                            "text": "주문수량",
                                            "x": 0.05,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"fixedrange": True},
                                        "yaxis": {"fixedrange": True},
                                        "colorway": ["#E12D39"],
                                    },
                                },
                            ),
                            className="card",
                        ),
                    ],
                    className="wrapper"
            ),
        ],
    )

    
from dash.dependencies import Output, Input


@app.callback(
    [Output("order", "figure"),Output("price", "figure")],
    [
        Input("region", "value"),
        Input("type-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)

def update_charts(gu, 카테고리명, start_date, end_date):
    mask = (
        (data.gu == gu)
        & (data.카테고리명 == 카테고리명)
        & (data.주문일시 >= start_date)
        & (data.주문일시 <= end_date)
    )
    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["주문일시"],
                "y": filtered_data["판매가"],
                "type": "lines",
                "hovertemplate": "%{y:.2f}₩<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "주문 판매액",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "₩", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["주문일시"],
                "y": filtered_data["수량"],
                "type": "bar",
            },
        ],
        "layout": {
            "title": {
                "text": "주문 건수",
                "x": 0.05,
                "xanchor": "left"
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure

if __name__ == "__main__":
    app.run_server(debug=True)
    
