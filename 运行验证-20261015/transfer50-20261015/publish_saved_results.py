"""Describe and plot audited saved results. No model import, inference, or trading."""
from pathlib import Path
import hashlib
import json
import os
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR'] = str(ROOT.parent / '.cache/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.text import Text
import numpy as np

s = json.loads((ROOT / 'results/summary.json').read_text())
a = json.loads((ROOT / 'independent-artifact-audit.json').read_text())
p = json.loads((ROOT / 'results/per-symbol-descriptive.json').read_text())
launch = json.loads((ROOT / 'launch-attempt.json').read_text())
old = json.loads((ROOT.parent / 'results/summary.json').read_text())
assert a['status'] == 'PASS' and s['complete_panel'] and launch['child_exit_code'] == 0
assert s['n_records'] == 9400 and s['n_complete_time_windows'] == 188 and len(p) == 50
assert not s['gate_passed'] and not a['profitability_established']
better = sum(v['relative_mse_improvement'] > 0 for v in p.values())
worse = sum(v['relative_mse_improvement'] < 0 for v in p.values())
ties = len(p) - better - worse
assert (better, worse, ties) == (7, 43, 0)
now = datetime.now(timezone.utc).isoformat()

review = {
    'recorded_at_utc': now,
    'reviewer': '/root/audit_188_evaluation',
    'basis': 'direct independent read-only review of actual completed summary, state, launch, artifact audit, frozen protocol and per-symbol files',
    'verdict': 'execution_and_artifact_audit_complete_prediction_gate_failed',
    'checked_records': 9400, 'synchronous_windows': 188, 'symbols': 50,
    'required_limits': [
        '4.074059% is relative MSE difference, not capital loss, ROI or price percentage error',
        'negative CI is conditional on fixed panel and predeclared time-block method',
        '7 better point estimates are descriptive; no profitable stock selection',
        'same time period and supplier do not causally identify model versus input/data problems',
        'no fees, fills, net profit, drawdown, capacity or wealth proof'],
    'new_model_runs_by_review': 0, 'reviewer_modified_files': False}
(ROOT / 'completed-result-independent-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')

font = FontProperties(fname='/System/Library/Fonts/STHeiti Medium.ttc')
plt.rcParams['axes.unicode_minus'] = False
fig = plt.figure(figsize=(14, 14.8), facecolor='#f6f8fb')
grid = fig.add_gridspec(2, 2, height_ratios=[.72, 2.1], hspace=.39, wspace=.25)
fig.subplots_adjust(left=.075, right=.965, bottom=.095, top=.875)
fig.suptitle('50股固定检验：预测门槛未通过', x=.075, ha='left', y=.974, fontsize=25, fontweight='bold', color='#192b3d')
fig.text(.075, .935, '9,400条预测记录｜188个同步时间窗口｜Kronos-small 固定权重与参数', fontsize=13, color='#526271')
fig.text(.075, .908, '已完成源数据与计分独立核验；图中全部数值是预测误差，不是交易收益。', fontsize=12, color='#526271')

ax = fig.add_subplot(grid[0, 0])
idx = [100, 100 * s['model_mse'] / s['zero_mse']]
ax.bar(['不变价格基准', 'Kronos-small'], idx, width=.54, color=['#849bad', '#bd614b'])
for i, v in enumerate(idx):
    ax.text(i, v + 3, f'{v:.2f}', ha='center', fontsize=15, fontweight='bold')
ax.set_ylim(0, 130)
ax.set_title('整体平方误差高4.07%', loc='left', fontsize=17, pad=16)
ax.set_ylabel('误差指数：基准=100，越低越好', fontsize=11)
ax.grid(axis='y', alpha=.15)
ax.set_axisbelow(True)

ax = fig.add_subplot(grid[0, 1])
mean = s['paired_d_mean'] * 1e5
lo, hi = np.array(s['circular_block_bootstrap_95CI']) * 1e5
ax.axvline(0, color='#667b8d', linestyle='--', lw=1.2)
ax.errorbar(mean, .5, xerr=[[mean-lo], [hi-mean]], fmt='o', color='#bd614b', capsize=9, markersize=10, elinewidth=3)
ax.text(mean, .73, f'均值 {mean:.3f}', ha='center', fontsize=14, fontweight='bold')
ax.text(mean, .25, f'95%区间 [{lo:.3f}, {hi:.3f}]', ha='center', fontsize=12)
ax.set_xlim(-4.7, 1.2)
ax.set_ylim(0, 1)
ax.set_yticks([])
ax.set_title('误差改善的区间全部低于0', loc='left', fontsize=17, pad=16)
ax.set_xlabel('基准MSE − 模型MSE（乘以10^-5）；大于0才改善', fontsize=11)
ax.grid(axis='x', alpha=.15)

symbols = sorted(p)
for col in range(2):
    ax = fig.add_subplot(grid[1, col])
    names = symbols[col*25:(col+1)*25]
    vals = [p[k]['relative_mse_improvement'] * 100 for k in names]
    yy = np.arange(25)
    ax.barh(yy, vals, height=.64, color=['#3b8c7c' if v > 0 else '#bd614b' for v in vals])
    ax.set_yticks(yy, names)
    ax.invert_yaxis()
    ax.axvline(0, color='#788896', lw=.9)
    ax.set_xlim(-18.5, 6.0)
    for y, v in zip(yy, vals):
        ax.text(v + (.23 if v >= 0 else -.23), y, f'{v:+.2f}%', va='center', ha='left' if v >= 0 else 'right', fontsize=9)
    ax.set_xlabel('各股MSE改善率：正值较好，负值较差（%）', fontsize=11)
    ax.set_title('逐股描述，按代码字母排列' if col == 0 else '7只较好／43只较差：均为点估计', loc='left', fontsize=16, pad=14)
    ax.grid(axis='x', alpha=.12)
    ax.set_axisbelow(True)
for ax in fig.axes:
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=10)
fig.text(.075, .052, '每次输入过去80根交易柱，预测随后12根的终点；目标区间不重叠，历史输入有重叠。', fontsize=11, color='#526271')
fig.text(.075, .030, '逐股结果未作独立验证，不能事后挑7只作为策略；未检验成交、费用、滑点、回撤或容量。', fontsize=11, color='#526271')
for txt in fig.findobj(Text):
    size, weight = txt.get_fontsize(), txt.get_fontweight()
    txt.set_fontproperties(font)
    txt.set_fontsize(size)
    txt.set_fontweight(weight)
fig.savefig(ROOT / 'results/transfer50-evaluation.png', dpi=155, facecolor=fig.get_facecolor())
fig.savefig(ROOT / 'results/transfer50-evaluation.svg', facecolor=fig.get_facecolor())
plt.close(fig)

def link(name, rel):
    return f'[{name}](<{ROOT / rel}>)'

table = '\n'.join(f"| {k} | {v['n']} | {v['zero_mse']:.10f} | {v['model_mse']:.10f} | {v['relative_mse_improvement']*100:+.3f}% |" for k, v in sorted(p.items()))
text = f'''# Kronos-small：50股固定离线检验报告

报告日期：2026-10-15。执行于北京时间14:19:17开始、16:07:00结束；独立产物核验于16:09完成。新增付款0，本机CPU最多6线程；模型推理约107.37分钟，启动至退出约107.73分钟。没有训练、调参、连接账户或交易；原188窗及AAPL未来封存预测保持原件。

**结论：当前固定用法的预测门槛未通过。50只股票整体均方误差比“不变价格”基准高4.074%。在预先固定的时间区块方法及这份面板下，误差改善的95%区间完全低于0；前后两半也均较差。建议结束对这一配置的重复试错，不把它推进为投入交易资金的项目。**

这次确实复用了现成数据、公开权重和预测代码，在一天内取得完整负向检验证据。得到的成果是可核验的研究结论，尚未得到赚钱方法。没有证据把它放大到任何盈利规模，更没有缩短到Gerko财富1%的可证实路径。

![实际50股检验结果](<{ROOT / 'results/transfer50-evaluation.png'}>)

## 1. 实际完成了什么

人类授权的是一次固定评估：除已评估AAPL之外，使用固定研究文件中的全部50只股票；不选赢家，不换参数，不追加试验。推理前于北京时间14:18:59冻结代码、权重、数据、种子规则、指标和门槛。

| 项目 | 实际值与口径 |
|---|---|
| 覆盖 | 50/50只股票，188/188个共同时间窗口，9400/9400条预测记录；无缺失计划记录 |
| 数据 | Twelve Data研究发布 `financial-world-model` 的 `bars_1h/test.parquet`；固定revision，不取得新行情 |
| 历史范围 | 原文件每股3113根，纽约2025-01-02 09:30至2026-10-13 15:30；目标从2025-07-01起，取全部188个完整12柱窗口，尾部不足12柱的3根不评分 |
| 输入与目标 | 过去80根开、高、低、收价格，预测后12根交易柱的最后收盘价；缺成交量与金额按官方价格输入路径处理 |
| 模型 | 固定Kronos-small与Tokenizer权重，无训练、微调或参数选择；每窗固定10条抽样路径均值 |
| 基准 | 预测终点价格等于最后一根输入收盘价，即预测收益0 |
| 检验单位 | 188个同步时间窗口；同窗50股一起汇总、一起重抽样，不能把9400行当9400个独立样本 |
| 完整性 | 正常退出0，格式/日历QC通过；独立产物审计PASS；预测门槛FAILED |

“交易柱”不是自然小时：美股正常日有7根此类柱，末柱可仅30分钟；12根会跨隔夜、周末或节假日。相邻目标不重叠，80柱历史仍重叠。

依据：{link('冻结协议', 'protocol.json')}、{link('执行回执', 'launch-attempt.json')}、{link('实际运行设置', 'results/runtime.json')}、{link('授权范围', 'authorization.json')}。

## 2. 完整结果与统计口径

均方误差（MSE）就是把每次预测错开的幅度平方后取平均，错得特别远会被加重惩罚。为使不同股价可比较，预测和实际均换算为相对输入末价的收益：`r=实际终价/p0−1`，`r_hat=预测终价/p0−1`。

| 主结果 | 数值 |
|---|---:|
| 不变价格基准MSE | {s['zero_mse']:.13f} |
| 模型MSE | {s['model_mse']:.13f} |
| 模型MSE相对基准 | **高{-s['relative_mse_improvement']*100:.6f}%** |
| 平均配对改善量d | {s['paired_d_mean']:.10f} |
| d的95%区间 | [{s['circular_block_bootstrap_95CI'][0]:.10f}, {s['circular_block_bootstrap_95CI'][1]:.10f}] |
| 前半/后半平均d | {s['chronological_halves_mean_d'][0]:.10f} / {s['chronological_halves_mean_d'][1]:.10f} |
| 逐股MSE点估计 | 7只低于基准，43只高于基准，0只持平 |

定义：`d=r²−(r_hat−r)²`。d正数代表模型平方误差更低。先每个时间窗对50股等权平均，再在时间维度汇总；总改善率按总MSE之比计算，不是逐股改善百分比平均。较高波动资产仍会贡献较大平方误差。

区间使用事先冻结的循环时间区块bootstrap（按连续时间段重抽样以保留部分相关性）：块长10个时间窗口、5000次、95%、种子20261015。结果依赖此相关性处理假设及当前固定面板，不能外推所有市场和用法。

原通过条件是完整QC及全部记录成立、d区间下界大于0、前后两半d均大于0。QC与记录完整性通过；区间下界和前后两半的改善要求均未通过。不是因为预算不足、记录没跑齐或结果仅仅未达到严格的置信度要求。

**高4.07%指MSE相对高4.07%，不是本金亏损4.07%，不是收益率，也不是每个价格都错4.07%。**本次未检验方向或选股收益的主张，不把MSE失败改名为另一项成功。

依据：{link('完整主结果', 'results/summary.json')}、{link('独立重算与原件保全核验', 'independent-artifact-audit.json')}、{link('9400条保存预测', 'results/predictions.jsonl')}。

## 3. 与原AAPL188窗相比，证据改变了什么

| 检验 | 原AAPL | 本次其余50股 |
|---|---|---|
| 记录/共同时间窗口 | 188 / 188 | 9400 / 188 |
| 模型MSE相对基准 | 高{-old['relative_mse_improvement']*100:.2f}% | 高{-s['relative_mse_improvement']*100:.2f}% |
| d的95%区间 | 跨0，未证明优于，也不能据此判显著较差 | 完全低于0，在预设方法下平方误差显著较差 |
| 分段 | 前后两半均负 | 前后两半均负 |

新结果削弱了“只是AAPL这一只股票碰巧不合适”的解释；相同设置在全部新增50股的平均表现仍不支持优势。它们和AAPL共享供应商与市场时段，不能简单相加当作9588个独立试验，也没有扩大到独立的市场年代。

7只的较好结果只是事后逐股点估计，未作逐股显著性、多重比较或独立留出确认。看完结果再选这7只，会改变原问题并引入选择偏差，不能称为已经发现可赚钱股票。

原结果保持独立：[{ROOT.parent.name}中的首轮报告](<{ROOT.parent / '首轮真实评估报告-20261015.md'}>)。

## 4. 能否区分模型没优势，还是数据、输入、评估有问题

| 原因候选 | 当前证据 | 可以/不可以下的结论 |
|---|---|---|
| 切片、价格映射或计分错误 | 独立脚本逐条从原Parquet重建9400条历史输入指纹、p0、实际终点及误差，并重算统计；全部一致 | 未发现足以推翻结果的此类错误；不等于数学上证明代码绝无错误 |
| 实际跑错权重/参数或遗漏 | 冻结身份、运行身份、全部记录、种子及顺序核验一致；模型与Tokenizer均eval，训练步数0 | 没有证据以重跑或换种子修正结果 |
| 只有价格，没有量额 | 作者有价格四字段路径，论文披露量额置0训练；本次不是完整六字段复现 | 不足以判无效调用；也不能断言补量额必然改善，当前没有这个对照 |
| 供应商数值/时间语义 | 格式、正价格、OHLC关系和共同日历通过；历史首发时点/修订、跨市场训练时区规范未完整重建 | 同一数据源的共同问题仍可能影响所有股票；审计不能替代交易所准确性审计 |
| 已发现量价差异 | 先前单日小时量合计与Apple IR约差2.95倍，价格也有小差异，原因未定位 | 量未输入，不能拿它直接解释当前失败；价格差异的全期影响仍UNKNOWN |
| 模型对本任务没有增量 | 固定50股总体MSE较差且两半均负 | 支持“当前固定用法未显示优势”；不唯一识别模型本体、输入或数据各自贡献 |
| 训练/测试污染 | 论文称预训练截至2024年6月；固定公开权重早于本次2025年7月起目标 | 时间顺序成立；完整训练清单、日志与具体权重绑定仍未独立核实；文件名test不构成保证 |

这是**回顾性跨股票扩展检验**。股票名单是现成大盘股面板，非当时全市场成分重建，仍有选择/存活偏差限制；历史数据在当时是否及时可得也未重建。没有构造真正前瞻的可成交交易。

来源：{link('独立核验', 'independent-artifact-audit.json')}、[此前数据与输入说明](<{ROOT.parent / 'Kronos-small-188窗口归因与加速验证判断-20261015.md'}>)；作者[论文v1](https://arxiv.org/html/2508.02739v1)发表于2025-08-02，代码固定[提交](https://github.com/shiyu-coder/Kronos/blob/67b630e67f6a18c9e9be918d9b4337c960db1e9a/model/kronos.py)，资料读取日期2026-10-15。公开权重并不等于完整训练审计。

## 5. 对“复制XTX一环，并赚钱放大”的判断

**已复制的环节：**用现成合法研究数据和公开固定模型，把输入变成预测，预先定基准，再独立核对。实际约108分钟、付款0完成了这轮筛选；不需要从零训练或自行积累多年行情。

**未复制成功的环节：**这套输入和模型尚未展示足以支持投入资金的预测优势。我们没有XTX私有模型或策略的等价证明；Kronos也不是已知的XTX模型。

从预测走到财富仍缺少：可重复且可利用的优势、事先固定的交易决策、可成交性、费用与滑点后净收益、不同市场阶段样本外表现、回撤与尾部风险，以及随交易规模增加后的容量。此处是证据链缺口，不表示每个盈利策略都必须先赢终点MSE；MSE更好也不能保证赚钱。

**当前建议：该固定配置停止重复试错；保留作知识与方法研究，当前不作为独立赚钱项目推进。**不因7只点估计较好而选股，不因总体失败而自动反着做，也不继续换种子、期限或指标直到出现好看结果。只有出现一个具体且能独立验证的差异依据，例如可靠的输入/供应商规范发现，才有理由另定一次新检验；本报告不启动它。

作者论文的A股多股票日线投资模拟与本次美股小时终点MSE任务不同；本次不是论文收益复现，也不能从作者模拟直接继承盈利。此轮未测净收益、回撤与容量，因此“能放大到多少钱”和“距离1%财富的资金倍数路径”均UNKNOWN。

单次未来封存AAPL预测仍独立保留，目标柱结束时间为北京时间10月16日02:30；截至本报告仍未到期、未评分。它只会按原规则在同供应商完整数据确认后评分，不重跑模型，不与本次统计混合。

## 6. 全部50股描述性结果（按字母排列，不筛赢家）

“改善率”正值仅指该股MSE点估计较低。逐股结果未作可交易性、独立显著性或多重比较确认，不是股票推荐或策略收益。

| 股票 | 窗口数 | 基准MSE | 模型MSE | MSE改善率 |
|---|---:|---:|---:|---:|
{table}

## 7. 可追溯原件与未确认事项

- {link('冻结协议', 'protocol.json')}；SHA256 `e2ead12911870a000e81e3a30a2eaed3e6e2ec1effb0bf8871a84941cebbf346`。
- {link('主结果', 'results/summary.json')}；SHA256 `36720392e1ebcf135c63b065b74458cbbb7279be27a632c0cee948bba6c7655f`。
- {link('完整预测记录', 'results/predictions.jsonl')}；SHA256 `8027eda08316727f752c5b6eb191388746afe4dacb34a330a92308f0bf1255d1`。
- {link('独立产物审计', 'independent-artifact-audit.json')}；SHA256 `3bbba41df0edc547d717f4b48b0eda20b43e9832b457378efe9fc5a119f99351`。PASS指来源映射、保存和计分一致，预测门槛另为false。
- {link('全部逐股描述', 'results/per-symbol-descriptive.json')}；{link('实际结果人工审阅回执', 'completed-result-independent-review.json')}。
- 数据研究许可依据见[此前授权与资源核验](<{ROOT.parent / 'evidence/authorization-license-resource.json'}>)，限私人、非商业、非生产的离线研究；不是实盘或任意再分发许可。
- UNKNOWN：完整训练清单及权重绑定、逐条交易所准确性、历史首发/修订、跨市场训练时区细则，以及任何可执行净收益/回撤/容量。没有用通用行业知识填补这些证据。

报告和图仅读取已有结果，不导入或运行模型。所有原协议、原预测、权重、数据及未来封存点均保留；没有自动追加实验。整体财富目标尚未达成。
'''
report_path = ROOT / '50股真实评估报告-20261015.md'
report_path.write_text(text)

status = {
    'checked_at_utc': now,
    'previous_goal_turn_classification': 'verified_wait on the same single authorized execution',
    'current_goal_turn_classification': 'meaningful_progress: completed one fixed model evaluation, independent artifact audit, and report',
    'execution_status': 'completed', 'exec_session_id': 52330,
    'child_exit_code': 0, 'live_model_process': False,
    'n_records': 9400, 'n_common_time_windows': 188, 'n_symbols': 50,
    'completed_real_artifact_audit': 'PASS', 'prediction_gate': 'FAILED',
    'relative_mse_improvement': s['relative_mse_improvement'],
    'goal_achieved': False, 'goal_status': 'active',
    'new_payments': 0, 'trades': 0, 'additional_model_starts_after_completed_run': 0,
    'report': str(report_path),
    'next_action': 'No further model run automatically. Preserve this negative result. Independent future AAPL point remains under its existing one-time schedule; no trading or claim of profitability.'}
(ROOT / 'continuation-status.json').write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n')

prior_path = ROOT.parent / 'Kronos-small-188窗口归因与加速验证判断-20261015.md'
prior_text = prior_path.read_text()
old_note = prior_text.split('\n\n')[1]
assert old_note.startswith(('**续接状态（', '**当前结果（'))
new_note = f'**当前结果（2026-10-15北京时间16:09）：一次固定50股离线检验已正常结束，9400条记录完整，独立产物审计PASS，但预测门槛FAILED：模型MSE比不变价格基准高4.074%，配对改善量95%区间完全为负，前后两半也均负。**详见[50股完整报告](<{report_path}>)。以下正文保留为启动前研究与准备记录，其中“待允许”“未启动”及建议一次验证的句子属于历史阶段；当前不再是待运行状态。原188窗和AAPL未来封存预测仍独立保留，未追加模型试验或交易。'
prior_path.write_text(prior_text.replace(old_note, new_note, 1))

hashes = {}
for rel in ['results/summary.json', 'results/predictions.jsonl', 'results/per-symbol-descriptive.json', 'independent-artifact-audit.json', 'completed-result-independent-review.json', 'results/transfer50-evaluation.png', 'results/transfer50-evaluation.svg', report_path.name]:
    fp = ROOT / rel
    hashes[rel] = {'sha256': hashlib.sha256(fp.read_bytes()).hexdigest(), 'bytes': fp.stat().st_size}
(ROOT / 'report-manifest.json').write_text(json.dumps({'generated_at_utc': now, 'model_import_or_run': False, 'files': hashes}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'report': str(report_path), 'lower_point_estimates': better, 'higher_point_estimates': worse, 'ties': ties, 'plot': str(ROOT / 'results/transfer50-evaluation.png'), 'model_runs': 0}, ensure_ascii=False))
