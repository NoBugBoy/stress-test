from pyecharts.faker import Faker

import model.SyncRequest as sync
from pyecharts import options as opts
from pyecharts.charts import Bar

# 生成图表
fix_time = []


def fix_data():
    for fix in sync.response_time:
        fix_time.append(format(fix, '.2f'))


def show():
    fix_data()
    bar = Bar()
    bar.add_xaxis(sync.ids)
    bar.add_yaxis('线程', fix_time, stack="stack1", color=Faker.rand_color())
    bar.reversal_axis()
    bar.set_global_opts(title_opts=opts.TitleOpts(title="压测时间图"), datazoom_opts=opts.DataZoomOpts(orient="vertical"))
    bar.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="最大值"),
                opts.MarkPointItem(type_="min", name="最小值"),
                opts.MarkPointItem(type_="average", name="平均值"),
            ]
        )
    )
    bar.render('压力测试.html')
