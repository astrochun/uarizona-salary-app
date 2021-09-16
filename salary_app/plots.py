import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from bokeh.models import PrintfTickFormatter
from bokeh.plotting import figure, ColumnDataSource

from constants import SALARY_COLUMN, STR_N_EMPLOYEES, CURRENCY_NORM
from commons import add_copyright

TOOLTIPS = [
    ("(salary, %)", "($x, $y)"),
    ("name", "@name"),
]


def bokeh_fig_init(x_range: list, title: str = '', x_label: str = '',
                   y_label: str = '', bc: str = "#f0f0f0", bfc: str = "#fafafa",
                   tools: str = "xpan,xwheel_zoom,xzoom_in,xzoom_out,save,reset") -> figure:

    arg_keys = dict(locals())
    arg_keys['x_axis_label'] = arg_keys.pop('x_label')
    arg_keys['y_axis_label'] = arg_keys.pop('y_label')
    arg_keys['background_fill_color'] = arg_keys.pop('bc')
    arg_keys['border_fill_color'] = arg_keys.pop('bfc')

    s = figure(**arg_keys)

    # Add copyright
    l1 = add_copyright()
    s.add_layout(l1)

    return s


def bokeh_scatter(x, y, name, pay_norm: int = 1,
                  x_label: str = '', y_label: str = '',
                  x_range: list = tuple([0, 500]), title: str = '',
                  bc: str = "#f0f0f0", bfc: str = "#fafafa",
                  fc="#f8b739", s: figure = None):

    if s is None:
        s = bokeh_scatter_init(pay_norm, x_label, y_label, title=title,
                               x_range=x_range, bc=bc, bfc=bfc)

    source = ColumnDataSource(data=dict(x=x, y=y, name=name))

    s.scatter('x', 'y', marker='circle', fill_color=fc, source=source,
              line_color='grey', alpha=0.25)

    return s


def bokeh_scatter_init(pay_norm: int, x_label: str, y_label: str,
                       title: str = '', x_range: list = None,
                       bc: str = "#f0f0f0", bfc: str = "#fafafa") -> figure:

    x_buffer = 1000 / pay_norm
    x_min = 10000 / pay_norm
    x_limit = 500000 / pay_norm
    if CURRENCY_NORM and pay_norm == 1:
        x_buffer /= 1e3
        x_min    /= 1e3
        x_limit  /= 1e3

    if pay_norm != 1:
        x_label = 'Hourly Rate'

    if x_range is None:
        x_range = [x_min - x_buffer, x_limit + x_buffer]

    s = figure(title=title,
               x_axis_label=x_label,
               y_axis_label=y_label,
               x_range=x_range,
               background_fill_color=bc,
               border_fill_color=bfc,
               tools=["pan,box_zoom,hover,save,reset"],
               tooltips=TOOLTIPS,
               )

    if CURRENCY_NORM and pay_norm == 1:
        s.xaxis[0].formatter = PrintfTickFormatter(format="$%ik")
    else:
        if pay_norm > 1:
            s.xaxis[0].formatter = PrintfTickFormatter(format="$%i")
        else:
            s.xaxis[0].formatter = PrintfTickFormatter(format="$%i")

    return s


def bokeh_histogram(x, y, pay_norm, x_label: str, y_label: str,
                    x_range: list, title: str = '',
                    bc: str = "#f0f0f0", bfc: str = "#fafafa"):

    bin_size = x[1] - x[0]

    s = figure(title=title,
               x_axis_label=x_label,
               y_axis_label=y_label,
               x_range=x_range,
               background_fill_color=bc,
               border_fill_color=bfc,
               tools=["xpan,xwheel_zoom,xzoom_in,xzoom_out,save,reset"]
               )

    # Add copyright
    l1 = add_copyright()
    s.add_layout(l1)

    s.vbar(x=x, top=y, width=0.95*bin_size, fill_color="#f8b739",
           fill_alpha=0.5, line_color=None)
    if CURRENCY_NORM and pay_norm == 1:
        s.xaxis[0].formatter = PrintfTickFormatter(format="$%ik")
    else:
        s.xaxis[0].formatter = PrintfTickFormatter(format="$%i")
    st.bokeh_chart(s, use_container_width=True)


def altair_histogram(x, y, pay_norm, x_label: str, y_label: str,
                     x_range: list, title: str = ''):

    data_dict = dict()
    data_dict[SALARY_COLUMN] = x

    data_dict[STR_N_EMPLOYEES] = y
    salary_df = pd.DataFrame(data_dict)
    tooltip = [SALARY_COLUMN, STR_N_EMPLOYEES]

    alt_x = alt.X(f'{SALARY_COLUMN}:Q',
                  scale=alt.Scale(domain=x_range, nice=False))
    c = alt.Chart(salary_df).mark_bar().encode(
        alt_x, y=STR_N_EMPLOYEES, tooltip=tooltip).interactive()
    st.altair_chart(c, use_container_width=True)


def bin_data(bin_size: int, pay_norm: int, min_val: float = 10000,
             max_val: float = 2.5e6):

    bins = np.arange(min_val/pay_norm, max_val/pay_norm, bin_size)
    if CURRENCY_NORM and pay_norm == 1:
        bins /= 1e3
    return bins


def histogram_plot(data, bin_size, pay_norm: int, bokeh=True):

    bins = bin_data(bin_size, pay_norm)

    x_buffer = 1000 / pay_norm
    x_limit = 500000 / pay_norm
    sal_data = (data[SALARY_COLUMN] / pay_norm).copy()
    if CURRENCY_NORM and pay_norm == 1:
        sal_data /= 1e3
        x_buffer /= 1e3
        x_limit /= 1e3

    if pay_norm == 1:
        x_label = SALARY_COLUMN
    else:
        x_label = 'Hourly Rate'

    N_bin, salary_bin = np.histogram(sal_data, bins=bins)
    x_range = [min(bins) - x_buffer,
               min([max(sal_data) + x_buffer, x_limit])]
    if not bokeh:
        altair_histogram(salary_bin[:-1], N_bin, pay_norm,
                         x_label=x_label, y_label=STR_N_EMPLOYEES,
                         x_range=x_range)
    else:
        bokeh_histogram(salary_bin[:-1], N_bin, pay_norm,
                        x_label=x_label, y_label=STR_N_EMPLOYEES,
                        x_range=x_range)


def percentile_plot(data, bin_size, same_title: np.ndarray = None,
                    title_changed: np.ndarray = None,
                    bc: str = "#f0f0f0", bfc: str = "#fafafa"):

    bins = np.arange(-50, 250.0, bin_size)

    x_label = 'Percentage'

    bin_size = bins[1] - bins[0]

    x_range = [-10, 25]

    s = figure(x_axis_label=x_label,
               y_axis_label=STR_N_EMPLOYEES,
               x_range=x_range,
               background_fill_color=bc,
               border_fill_color=bfc,
               tools=["xpan,xwheel_zoom,xzoom_in,xzoom_out,save,reset"]
               )

    # Add copyright
    l1 = add_copyright()
    s.add_layout(l1)

    N_bin, percent_bin = np.histogram(data, bins=bins)

    s.vbar(x=percent_bin[:-1], top=N_bin, width=0.95*bin_size,
           fill_color=None, fill_alpha=0.5, line_color='black',
           legend_label='All')

    if same_title is not None:
        N_bin1, percent_bin1 = np.histogram(data[same_title], bins=bins)

        s.vbar(x=percent_bin1[:-1], top=N_bin1, width=1.0 * bin_size,
               fill_color="#f8b739", fill_alpha=0.5, line_color=None,
               legend_label='Unchanged')

    if title_changed is not None:
        N_bin2, percent_bin2 = np.histogram(data[title_changed], bins=bins)

        s.vbar(x=percent_bin2[:-1], top=N_bin2, width=1.0 * bin_size,
               fill_color="purple", fill_alpha=0.5, line_color=None,
               legend_label='Changed')

    s.legend.orientation = 'vertical'
    s.legend.location = 'top_right'

    st.bokeh_chart(s, use_container_width=True)
