# 三份固定成交档案footer独立审阅

限定PASS，material_errors=[]。UTC：2026-10-16T16:23:54.711864+00:00。实际model/effort UNKNOWN，规则版本不变。

现有项目PyArrow26仅被动解析原始footer metadata；未读数据行、未联网、未运行来源代码/SQL/SDK/EVM/模型/回测/策略/交易。

| 文件 | 声明全文件bytes | 行数 | rowgroups | 可能含目标区间的组 |
|---|---:|---:|---:|---|
| data_0 | 299909858 | 5244226 | 5 | [0, 1, 2, 3, 4] |
| data_1 | 510358267 | 8877881 | 10 | [0, 1, 3] |
| data_2 | 44357671 | 758117 | 2 | [] |

六份原响应均206；实际保存53846B。原件SHA/bytes、固定revision URL、ContentRange几何、尾部PAR1/小端长度、footer末8B、同文件ETag与If-Range逐项一致。独立核16列、全部列chunk位置/压缩尺寸/统计及各组行数，与root派生吻合；所有chunk在声明数据区内且连续到footer。没有完整文件内容SHA或数据页核验。

data_0/data_1的block统计可能覆盖固定六tx所在86161952—86161969；data_2的两组最小块均大于目标上界，因此在统计可信条件下不覆盖。可能覆盖不等于精确六tx命中，统计min/max不证明中间每块/交易存在，分组重叠也不能当顺序完整性。未取得行不能填价格或费用，更不能升级盈利准入。

所有实际输入绝对路径/SHA/bytes、原始block ranges和每文件绑定结果见同名JSON。此审阅不修改root或既有解释note。
