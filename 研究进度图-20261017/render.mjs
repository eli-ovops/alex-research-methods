import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import crypto from 'node:crypto';
import sharp from '/Users/USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.mjs';
const dir=path.dirname(fileURLToPath(import.meta.url));
const C={bg:'#F7F5EF',ink:'#152B41',muted:'#596979',green:'#167B6B',greenBg:'#E2EFE7',amber:'#A15F12',amberBg:'#F6E7C9',gray:'#74818A',grayBg:'#E9ECEB',white:'#FFFFFF'};
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;');
const text=(x,y,s,size=32,color=C.ink,weight=400,extra='')=>`<text x="${x}" y="${y}" font-size="${size}" fill="${color}" font-weight="${weight}" ${extra}>${esc(s)}</text>`;
const box=(x,y,w,h,fill,rx=18)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}"/>`;
const line=(x,y,x2,y2,c='#D7DEDC')=>`<path d="M${x} ${y}H${x2}" stroke="${c}" stroke-width="2"/>`;
function base(n,title,sub,body,foot){return `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100" viewBox="0 0 1600 1100"><style>text{font-family:'PingFang SC','Hiragino Sans GB','Arial',sans-serif}</style>${box(0,0,1600,1100,C.bg,0)}${text(72,70,'研究进度 / '+n+' OF 03',24,C.green,600)}${text(1528,70,'截至 2026-10-17',24,C.muted,400,'text-anchor="end"')}${text(72,150,title,52,C.ink,600)}${text(72,206,sub,28,C.muted)}${body}${line(72,1008,1528,1008)}${text(72,1052,foot,23,C.muted)}</svg>`;}
let b='';
b+=box(72,246,1456,114,C.ink);b+=text(102,291,'长期目标',24,'#B7D6D0',600);b+=text(102,337,'借鉴可复制环节，长期争取达到 Gerko 财富的 1%',38,C.white,500);
const rows=[['01','XTX 公开赚钱机制','已研究','私人策略未公开',C.green,C.greenBg],['02','可核对的研究流程','已建立','免费数据 · 固定评估 · 封存 · 独立核查',C.green,C.greenBg],['03','价格预测优势','当前未通过','Kronos 与 BTC 固定模型路径未通过',C.amber,C.amberBg],['04','个人持续扣费盈利','未证明','预测误差不能直接换算为净利润',C.gray,C.grayBg],['05','资金容量与财富积累','未证明','放大仍有效、资本积累与个人所有权',C.gray,C.grayBg]];
rows.forEach((r,i)=>{const y=392+i*116;b+=box(72,y,1456,100,i===2?C.amberBg:C.white);b+=text(103,y+62,r[0],34,r[4],600);b+=text(184,y+44,r[1],32,C.ink,600);b+=text(184,y+80,r[3],24,C.muted);b+=text(1488,y+61,r[2],30,r[4],600,'text-anchor="end"');});
const svg1=base('01','我们要到哪里，现在在哪里','当前沿价格预测模型主线推进；本轮诊断已完成。',b,'阶段进度不能换算为财富目标完成比例。个人持续可复制净盈利仍未证明。');
b='';
b+=box(72,246,1456,104,C.greenBg);b+=text(104,290,'最终权重能够粗略跟价',33,C.green,600);b+=text(104,330,'但训练集也没有胜过“下一价格不变”这个简单基准。',29,C.ink);
b+=text(92,410,'MSE / 同期不变价格基准',31,C.ink,600);b+=text(92,450,'均方预测误差 · 越低越好',25,C.muted);
b+=text(946,406,'训练集',31,C.ink,600,'text-anchor="middle"');b+=text(946,447,'11,950 个窗口',25,C.muted,400,'text-anchor="middle"');b+=text(1325,406,'原封存测试集',31,C.ink,600,'text-anchor="middle"');b+=text(1325,447,'2,972 个窗口',25,C.muted,400,'text-anchor="middle"');
[['不变价格基准','1.00','1.00',C.greenBg,C.green],['LSTM 价格版','8.89','35.27',C.white,C.ink],['LSTM 加挂单压力版','8.35','34.95',C.white,C.ink]].forEach((r,i)=>{let y=482+i*124;b+=box(72,y,1456,108,r[3]);b+=text(104,y+65,r[0],33,r[4],600);b+=text(946,y+71,r[1],49,r[4],600,'text-anchor="middle"');b+=text(1325,y+71,r[2],49,r[4],600,'text-anchor="middle"');});
b+=text(86,916,'约 35 倍是平方误差倍数，不是亏损倍数，也不是收益率。',34,C.amber,600);b+=text(86,965,'两列各自使用同期基准；本轮没有计算实盘盈亏。',26,C.muted);
const svg2=base('02','能粗略跟价，还没有分钟预测优势','用已保存的 LSTM（序列神经网络）检查训练数据；没有重新训练。',b,'训练前向已完成；测试仅读取旧封存结果，未重跑。窗口有重叠，不等于独立试验次数。');
b='';
b+=box(72,246,708,350,C.greenBg);b+=text(104,300,'已核实',33,C.green,600);b+=text(104,360,'训练前向与独立评分已完成',32,C.ink,600);b+=text(104,416,'索引、缩放、权重加载、误差算术',28);b+=text(104,460,'未发现实质错误',28);b+=text(104,524,'权重与测试原件未变',28);b+=text(104,566,'本轮：0 重训 · 0 交易 · 新增付款 0',25,C.green,600);
b+=box(804,246,724,350,C.amberBg);b+=text(836,300,'仍未决',33,C.amber,600);b+=text(836,360,'训练、优化、结构，谁造成失败？',31,C.ink,600);b+=text(836,416,'历史学习曲线缺失，无法唯一归因',28);b+=text(836,460,'挂单压力本身是否有效，仍未知',28);b+=text(836,524,'旧岭回归 9 条数值警告仍待核',27,C.amber,500);b+=text(836,566,'警告在 LSTM 输出之后，不能解释其 35 倍',24,C.muted);
b+=box(72,630,1456,142,C.ink);b+=text(104,680,'当前决策 / 保留这份固定配置的负面研究样本',32,'#FFFFFF',600);b+=text(104,735,'不进入交易开发，不盲目加算力调参。',38,'#FFFFFF',600);
b+=text(72,829,'到财富目标还缺的三道门',28,C.muted,500);
[['独立时期优势','01'],['全成本净利润','02'],['放大仍有效','03']].forEach((r,i)=>{const x=72+i*494;b+=box(x,858,468,111,C.grayBg);b+=text(x+26,901,r[1],23,C.gray,600);b+=text(x+26,944,r[0],32,C.ink,600);});
const svg3=base('03','当前卡点：预测优势未成立，主因未定位','本轮诊断及独立验收均已完成；没有实验正在执行。',b,'本轮只评价预测误差，无实盘盈亏。不能据此否定所有模型或订单簿信息。');
const names=['01-goal-roadmap','02-evidence-results','03-blockers-decision'];const svgs=[svg1,svg2,svg3];
const manifest=[];
for(let i=0;i<3;i++){const file=path.join(dir,names[i]+'.svg');fs.writeFileSync(file,svgs[i]);await sharp(Buffer.from(svgs[i])).png().toFile(path.join(dir,names[i]+'.png'));}
fs.writeFileSync(path.join(dir,'index.html'),`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>研究进度图 · 2026-10-17</title><style>body{margin:0;background:#e9eceb;font-family:'PingFang SC',sans-serif;color:#152b41}header{padding:20px 4%;background:#f7f5ef;position:sticky;top:0;z-index:2}button{font:inherit;border:0;padding:8px 14px;background:#e2efe7;color:#167b6b;border-radius:7px;cursor:pointer}main{width:96%;max-width:1600px;margin:auto}section{margin:28px 0}svg{width:100%;height:auto;display:block}details{margin:30px 4%;line-height:1.8}a{color:#167b6b}</style><header><strong>研究进度 · 截至 2026-10-17</strong>　<button onclick="document.querySelector('main').style.maxWidth='1600px';document.querySelector('main').style.width='96%'">适应宽度</button> <button onclick="document.querySelector('main').style.maxWidth='none';document.querySelector('main').style.width='1600px'">原尺寸</button></header><main>${svgs.map((s,i)=>`<section id="figure-${i+1}">${s}<p><a href="${names[i]}.png">下载 PNG</a> · <a href="${names[i]}.svg">可编辑 SVG</a></p></section>`).join('')}</main><details><summary>数据来源与阅读边界</summary><p>来源：BTC训练集前向诊断-跟价能力与预测优势-20261017.md；BTC预测失败诊断-35倍误差从哪里来-20261017.md；XTX到个人财富目标-赚钱机制与证据收敛判断-20261016.md（仅目标与机制，旧下一步已被后续任务取代）。</p><p>训练/测试 MSE 精确倍数：价格版 8.8900 / 35.2701；挂单压力版 8.3538 / 34.9476。图中保留两位小数。训练集为模型见过的数据，并非新增样本外验证。没有独立验证集，不能唯一识别欠拟合、过拟合或优化问题；原始数据全部历史真值与实时可得性亦未完全闭合。</p><p>图3三道门是关键证据门槛摘要；最终财富仍涉及资本积累、税费与个人所有权。历史正现金片段不等于个人持续可复制净盈利。</p></details></html>`);
for(const name of [...names.flatMap(n=>[n+'.png',n+'.svg']),'index.html','render.mjs']){const buf=fs.readFileSync(path.join(dir,name));manifest.push({file:name,bytes:buf.length,sha256:crypto.createHash('sha256').update(buf).digest('hex')});}
fs.writeFileSync(path.join(dir,'manifest.json'),JSON.stringify({date:'2026-10-17',renderer:'SVG text + local sharp/libvips to PNG',dimensions:[1600,1100],targetModel:'gpt-6-astra',targetEffort:'medium',actualModel:'UNKNOWN',actualEffort:'UNKNOWN',files:manifest},null,2));
console.log(JSON.stringify(manifest,null,2));
