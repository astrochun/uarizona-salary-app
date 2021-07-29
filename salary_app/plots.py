import streamlit as st
from bokeh.plotting import figure, ColumnDataSource

TOOLTIPS = [
    ("(x,y)", "($x, $y)"),
    ("name", "@name"),
]


def bokeh_scatter(x, y, name, x_label: str, y_label: str,
                  x_range: list, title: str = '',
                  bc: str = "#f0f0f0", bfc: str = "#fafafa"):

    s = figure(title=title,
               x_axis_label=x_label,
               y_axis_label=y_label,
               x_range=x_range,
               background_fill_color=bc,
               border_fill_color=bfc,
               tools=["pan,box_zoom,hover,save,reset"],
               tooltips=TOOLTIPS,
               )

    source = ColumnDataSource(data=dict(x=x, y=y, name=name))

    s.scatter('x', 'y', marker='circle', fill_color="#f8b739", source=source)
    return s
    #st.bokeh_chart(s, use_container_width=True)
