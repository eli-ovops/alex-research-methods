"""Plot saved first-run errors only. Does not import or run the model."""
from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR'] = str(ROOT / '.cache/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.text import Text
import numpy as np

s = json.loads((ROOT / 'results/summary.json').read_text())
records = [json.loads(x) for x in (ROOT / 'results/predictions.jsonl').read_text().splitlines()]
font = FontProperties(fname='/System/Library/Fonts/STHeiti Medium.ttc')
fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.7), gridspec_kw={'width_ratios': [.85, 1.15]})
fig.patch.set_facecolor('#f5f7fa')
fig.subplots_adjust(left=.07, right=.98, top=.77, bottom=.24, wspace=.24)
fig.suptitle('首轮真实评估：AAPL｜固定 Kronos-small', fontsize=21, fontweight='bold', y=.97)
ax = axes[0]
vals = [s['zero_mse'] * 1e4, s['model_mse'] * 1e4]
ax.bar(['零收益基准', 'Kronos-small'], vals, color=['#8197aa', '#c66b4e'], width=.57)
ax.set_ylim(0, max(vals) * 1.3)
for i, v in enumerate(vals):
    ax.text(i, v + .09, f'{v:.4f}', ha='center', fontsize=14, fontweight='bold')
ax.set_title('本次点估计：误差高 4.18%', fontsize=15, pad=20)
ax.set_ylabel('均方误差（数值单位：0.0001；越低越好）', fontsize=11)
ax.set_axisbelow(True)
ax.grid(axis='y', alpha=.18)
for a in axes:
    a.spines[['top', 'right']].set_visible(False)
    a.tick_params(labelsize=11)
x = np.array([r['r'] for r in records]) * 100
y = np.array([r['r_hat'] for r in records]) * 100
ax = axes[1]
ax.scatter(x, y, s=25, alpha=.65, color='#527baa', linewidths=0)
lim = max(abs(x).max(), abs(y).max()) * 1.07
ax.plot([-lim, lim], [-lim, lim], '--', color='#bbc6d3', lw=1, label='预测完全准确')
ax.axhline(0, color='#8094a8', lw=.8)
ax.axvline(0, color='#8094a8', lw=.8)
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_xlabel('实际未来12根交易小时柱的收益（%）', fontsize=11)
ax.set_ylabel('模型预测收益（%）', fontsize=11)
ax.set_title('全部188个窗口：预测与实际', fontsize=15, pad=20)
ax.legend(loc='upper left', frameon=False, fontsize=10)
ax.grid(alpha=.15)
fig.text(.5, .095, '未通过预先设定的门槛；优势的95%区间跨0，不能断言显著更差。', ha='center', fontsize=13, color='#524b46')
fig.text(.5, .047, '回顾性时间外检验，固定权重、参数和种子；这不是实盘曲线、盈利证明或BTC验证。', ha='center', fontsize=10, color='#727b86')
for txt in fig.findobj(Text):
    size, weight = txt.get_fontsize(), txt.get_fontweight()
    txt.set_fontproperties(font)
    txt.set_fontsize(size)
    txt.set_fontweight(weight)
fig.savefig(ROOT / 'results/first-evaluation.png', dpi=155, facecolor=fig.get_facecolor())
fig.savefig(ROOT / 'results/first-evaluation.svg', facecolor=fig.get_facecolor())
print(json.dumps({'plotted_records': len(records), 'model_rerun': False}))
