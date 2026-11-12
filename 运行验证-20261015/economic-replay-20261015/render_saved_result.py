"""Render saved arithmetic results only. Does not import or run the replay."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt, font_manager, dates as mdates, patches

r = Path(__file__).resolve().parent
font = '/System/Library/Fonts/STHeiti Medium.ttc'
font_manager.fontManager.addfont(font)
name = font_manager.FontProperties(fname=font).get_name()
plt.rcParams.update({'font.family': [name, 'DejaVu Sans'], 'axes.unicode_minus': False,
                     'font.size': 10, 'svg.fonttype': 'path'})
cases = json.loads((r/'results/all-scenarios.json').read_text())
fig = plt.figure(figsize=(11.5, 8.8), facecolor='#f7f8fa')
gs = fig.add_gridspec(2, 1, height_ratios=[1.5, 1], left=.10, right=.94,
                     top=.86, bottom=.18, hspace=.42)
ax = fig.add_subplot(gs[0])
ax.set_facecolor('white')
first_time = final_time = None
for folder, label, color, lw in [
    ('commission0_slippage0bps', '前10名组合：零费用', '#2471a3', 1.7),
    ('benchmark', '50股等权参照：零费用', '#7a858f', 1.6),
    ('commission1_slippage5bps', '前10名组合：每笔$1＋单边5基点', '#c43d3d', 2.0)]:
    with (r/'results'/folder/'NAV-samples.jsonl').open() as f:
        data = [json.loads(x) for x in f]
    times = [datetime.fromisoformat(x['timestamp']) for x in data]
    nav = [x['NAV'] for x in data]
    first_time, final_time = times[0], times[-1]
    ax.plot(times, nav, label=label, color=color, lw=lw)
    ax.annotate(f'${nav[-1]:,.2f}', (times[-1], nav[-1]), xytext=(-6, 9),
                textcoords='offset points', ha='right', color=color, fontweight='bold')
ax.axhline(5000, ls='--', lw=.8, color='#aab0b6')
ax.set_ylabel('假设价格净值（美元）')
ny = ZoneInfo('America/New_York')
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3, tz=ny))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m', tz=ny))
ax.set_xlim(first_time, final_time)
ax.grid(axis='y', alpha=.15)
ax.legend(loc='lower left', frameon=False, fontsize=9)
ax.spines[['top', 'right']].set_visible(False)
ax2 = fig.add_subplot(gs[1])
arr = np.array([[cases[f'commission{c}_slippage{s}bps']['final_post_liquidation_cash_USD']
                 if cases[f'commission{c}_slippage{s}bps']['complete'] else np.nan
                 for s in [0, 5, 10]] for c in [0, 1, 2]])
cmap = plt.get_cmap('RdYlBu').copy()
cmap.set_bad('#dce0e5')
ax2.imshow(np.ma.masked_invalid(arr), cmap=cmap, vmin=1000, vmax=6500, aspect='auto')
for i, c in enumerate([0, 1, 2]):
    for j, s in enumerate([0, 5, 10]):
        x = cases[f'commission{c}_slippage{s}bps']
        text = (f"${x['final_post_liquidation_cash_USD']:,.2f}\n{x['hypothetical_price_NAV_return']:+.2%}"
                if x['complete'] else '现金约束停止\n无完整期末收益')
        ax2.text(j, i, text, ha='center', va='center', fontsize=10, color='#15222b')
ax2.add_patch(patches.Rectangle((.5, .5), 1, 1, fill=False, lw=3, edgecolor='#b02f2f'))
ax2.set_xticks([0, 1, 2], ['0基点', '5基点', '10基点'])
ax2.set_yticks([0, 1, 2], ['$0／笔', '$1／笔', '$2／笔'])
ax2.set_xlabel('单边滑点假设')
ax2.set_ylabel('每个净调仓股票指令的佣金')
ax2.set_title('固定9个费用情景：$5,000起步的期末值与区间收益', loc='left', fontsize=11, pad=10)
ax2.tick_params(length=0)
fig.text(.10, .945, '同一批封存预测，费用改变了什么？', fontsize=19, fontweight='bold', color='#162a3c')
fig.text(.10, .904, '主情景未通过候选筛选：假设价格净值5,000美元 → 2,093.32美元（−58.13%）',
         fontsize=12, color='#a32e2e')
fig.text(.10, .105, '纽约时间2025-07-01至2026-10-13；固定50股、每次前10名、188次调仓窗口。红框为预先指定主情景。', fontsize=9, color='#4b5660')
fig.text(.10, .073, '这是既有历史上的条件核算，不是实盘：行情口径、可成交性、实际券商费用与容量仍未确认。', fontsize=9, color='#4b5660')
fig.text(.10, .041, '50股参照为95%股票／5%现金的零费用数学组合；停止情景没有被填成零收益或破产。', fontsize=9, color='#4b5660')
for ext in ['png', 'svg']:
    fig.savefig(r/f'economic-replay-result.{ext}', dpi=170, facecolor=fig.get_facecolor())
plt.close(fig)
