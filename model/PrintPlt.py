from pyecharts.faker import Faker

import model.SyncRequest as sync
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie

# 生成图表
fix_time = []
fix_id = []


def fix_data():
    fix_time.clear()
    fix_id.clear()
    for fix in sync.response_time:
        fix_time.append(format(fix, '.2f'))
    for id in sync.ids:
        fix_id.append(id)


# 饼图分别显示成功 失败 限流数量
def show_pie(id):
    attr = ["成功（含熔断）", "失败", "限流"]
    counts = [len(sync.success), len(sync.fail), sync.limit]
    c = Pie(init_opts=opts.InitOpts(
                                width='1200px',
                                height='800px',
                                page_title='page'
                                ))
    c.add("", [list(attr) for attr in zip(attr, counts)])
    c.set_colors(["green", "red", "blue"])
    c.set_global_opts(title_opts=opts.TitleOpts(title="成功失败数量饼图"))
    c.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    c.render('成功失败数量饼图{}.html'.format(id + 1))


# 柱状图分别线程id和响应时间以及平均最大最小值
def show_bar(id):
    fix_data()
    bar = Bar(init_opts=opts.InitOpts(
                                width='1200px',
                                height='800px',
                                page_title='page'
                                ))
    bar.add_xaxis(fix_id)
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
    bar.render('压力测试{}.html'.format(id + 1))
