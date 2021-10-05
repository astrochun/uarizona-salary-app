from typing import Union, Optional

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from bokeh.models import PrintfTickFormatter, Label
from bokeh.plotting import figure, ColumnDataSource

from constants import SALARY_COLUMN, STR_N_EMPLOYEES, CURRENCY_NORM
from commons import add_copyright

TOOLTIPS = [
    ("(salary, %)", "($x, $y)"),
    ("name", "@name"),
]


def bokeh_fig_init(x_range: list, title: str = '', x_label: str = '',
                   y_label: str = '', bc: str = "#f0f0f0", bfc: str = "#fafafa",
                   tools: str = "xpan,xwheel_zoom,xzoom_in,xzoom_out,save,reset",
                   active_scroll: str = 'xwheel_zoom',
                   tooltips: list = None) -> figure:

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


def bokeh_scatter(x, y, name: pd.Series = None, pay_norm: int = 1,
                  x_label: str = '', y_label: str = '',
                  x_range: list = tuple([0, 500]), title: str = '',
                  size: Union[int, float] = 4,
                  bc: str = "#f0f0f0", bfc: str = "#fafafa",
                  fc="#f8b739", ec="#f8b739", alpha=0.5,
                  label: Optional[str] = None, s: figure = None):

    if s is None:
        s = bokeh_scatter_init(pay_norm, x_label, y_label, title=title,
                               x_range=x_range, bc=bc, bfc=bfc,
                               plot_constants=True)

    if name is not None:
        source = ColumnDataSource(data=dict(x=x, y=y, name=name))

        s.scatter('x', 'y', marker='circle', fill_color=fc, source=source,
                  line_color=ec, alpha=alpha, size=size, legend_label=label)
    else:
        s.scatter('x', 'y', marker='circle', fill_color=fc,
                  line_color=ec, alpha=alpha, size=size, legend_label=label)

    return s


def bokeh_scatter_init(pay_norm: int, x_label: str, y_label: str,
                       title: str = '', x_range: list = None,
                       bc: str = "#f0f0f0", bfc: str = "#fafafa",
                       plot_constants: bool = False) -> figure:

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

    s = bokeh_fig_init(x_range=x_range, title=title, x_label=x_label,
                       y_label=y_label, bc=bc, bfc=bfc,
                       tools="pan,wheel_zoom,box_zoom,hover,save,reset",
                       active_scroll='wheel_zoom', tooltips=TOOLTIPS)

    constants_level = [2500, 5000, 10000, 15000, 20000]

    if CURRENCY_NORM and pay_norm == 1:
        s.xaxis[0].formatter = PrintfTickFormatter(format="$%ik")
    else:
        if pay_norm > 1:
            s.xaxis[0].formatter = PrintfTickFormatter(format="$%i")
        else:
            s.xaxis[0].formatter = PrintfTickFormatter(format="$%i")

    if plot_constants:
        s = draw_constant_salary_bump(s, constants_level, pay_norm)

    return s


def bokeh_histogram(x, y, pay_norm, x_label: str, y_label: str,
                    x_range: list, title: str = '',
                    bc: str = "#f0f0f0", bfc: str = "#fafafa"):

    bin_size = x[1] - x[0]

    s = bokeh_fig_init(x_range=x_range, title=title, x_label=x_label,
                       y_label=y_label, bc=bc, bfc=bfc)

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


def bin_data_adaptive(data: list, index: np.ndarray,
                      bin_size: float, pay_norm: int,
                      min_val: float = 10000, max_val: float = 2.5e6,
                      N_min: int = 25):
    """
    Perform adaptive binning

    :param data: Data to bin
    :param index: Index for smallest sample selection
    :param bin_size: Minimum bin size
    :param pay_norm: Normalization to hours
    :param min_val: Minimum bin value
    :param max_val: Maximum bin value
    :param N_min: Minimum N in each bin

    :return:
    """

    arg_keys = dict(locals())
    for unused in ['data', 'index', 'N_min']:
        arg_keys.pop(unused)
    bins = bin_data(**arg_keys)

    N_bin, salary_bin = np.histogram(np.array(data)[index], bins)

    drops = []
    bad = np.where(N_bin < N_min)[0]
    for b in bad:
        if b not in drops and b != len(N_bin)-1:
            a = 0
            while True:
                drops.append(b + a + 1)
                N_bin[b] += N_bin[b+a+1]
                if N_bin[b] >= N_min or b+a+1 == len(N_bin)-1:
                    break
                else:
                    a += 1

    salary_bin = np.delete(salary_bin, drops)

    return salary_bin


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

    def _percent_norm(x):
        return x/len(data) * 100

    bins = np.arange(-50, 250.0, bin_size)

    x_label = 'Percentage'

    bin_size = bins[1] - bins[0]

    x_range = [-10, 25]

    s = bokeh_fig_init(x_range=x_range, x_label=x_label,
                       y_label='Percentage of Total Employees', bc=bc, bfc=bfc,
                       tools="xpan,xwheel_zoom,xzoom_in,xzoom_out,save,reset")

    N_bin, percent_bin = np.histogram(data, bins=bins)

    s.vbar(x=percent_bin[:-1], top=_percent_norm(N_bin), width=0.95*bin_size,
           fill_color=None, fill_alpha=0.5, line_color='black',
           legend_label='All')

    if same_title is not None:
        N_bin1, percent_bin1 = np.histogram(data[same_title], bins=bins)

        s.vbar(x=percent_bin1[:-1], top=_percent_norm(N_bin1),
               width=1.0 * bin_size, fill_color="#f8b739", fill_alpha=0.5,
               line_color=None, legend_label='Unchanged')

    if title_changed is not None:
        N_bin2, percent_bin2 = np.histogram(data[title_changed], bins=bins)

        s.vbar(x=percent_bin2[:-1], top=_percent_norm(N_bin2),
               width=1.0 * bin_size, fill_color="purple", fill_alpha=0.5,
               line_color=None, legend_label='Changed')

    s.legend.orientation = 'vertical'
    s.legend.location = 'top_right'

    st.bokeh_chart(s, use_container_width=True)


def draw_constant_salary_bump(s: figure, constant_list: list, pay_norm: int):
    """
    Draw lines for constant salary increase

    """

    constant_list0 = [c / pay_norm for c in constant_list]
    if CURRENCY_NORM and pay_norm == 1:
        constant_list0 = [a / 1e3 for a in constant_list]
        x_max = 2500.

    if pay_norm > 1:
        x_max = 1200.

    for c, constant in enumerate(constant_list0):
        x = np.arange(max([s.x_range.start, constant + 1]), x_max, 5)
        y = 100 * constant/(x-constant)

        if pay_norm == 1:
            text = f'${constant}k'
        else:
            text = f'${constant_list[c]/1e3}k (${constant:.2f}/hr)'

        source = ColumnDataSource(data=dict(x=x, y=y, name=[text] * len(x)))

        s.line('x', 'y', line_dash='dashed', line_color='black',
               source=source)

        y_label = constant_list[c]/1e3
        x_label = constant + 100 * constant / y_label

        label = Label(x=x_label, y=y_label, text=text)
        s.add_layout(label)

    return s
