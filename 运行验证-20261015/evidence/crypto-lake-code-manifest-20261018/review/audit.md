# 独立限定验收：固定客户端与匿名对象元数据

**PASS_LIMITED_STATIC_CLIENT_AND_ANONYMOUS_OBJECT_METADATA，无必须修正项。**当前可准备受限的单对象schema/时钟QC，不是已通过行情质量、预测或净盈利检验；本轮没有获取行情。

独立核固定完整tree42f0cc5fcf23a19050285d89cb4be075359f55af、main与5份API原件base64/惰性文本/Gitblob，均与tree一致；身份是tree，不冒commit或2022版本。源码、清单XML及小回执hash均一致。

main.py:56–77确实将sample.crypto.lake配置为UNSIGNED，_utils:105–118采用该config。三次明确BTC日期prefix的正常匿名GET均200，各KeyCount1、IsTruncatedfalse；首日HEAD200的Content-Length/ETag与list一致，公开对象version-id为wsEI9nFSmHryDvoX6arap5z6BRl9uz2v。另两对象未HEAD，version-id未知。ETag有multipart式后缀，不当内容hash；XML SHA只绑定metadata。

三对象267304100/282137927/328029311B，总877471338B压缩数据，约877.47MB；不是小文本或几行下载。LastModified只证对象元数据，非市场观测或历史即时可用时间。只有三个2022相邻日期，未证整日/连续性，不满足旧34日跨期方案。

客户端只做旧时间列rename/ns cast、Arrow索引/时区表示等；未在已审路径见特定received/origin时间回填或前移。concat(sort=False)不保证时间序，start/end只按日期含前不含后，row_slice是读回后的切片，不能限下载。当前客户端不能认证2022服务器collector/校正/快照生成，也未检查实际字段/时间/盘口。

UNSIGNED不是完整SDK绝不查询凭证的证明：main:120、231–252仍尝试session/Lambda登录，_read:145与_utils:39–49多文件路径也查session凭证。报告已保留此限度；本轮没有运行SDK或读取凭证。未来若做小QC不应盲跑load_data/示例或以row_slice冒下载上限。

前轮匿名内部研究的有限许可解释继续，不因metadata200变成任意再分发许可。可准备一个严格范围的原件QC，但不自动启动预测/收益实验，不改旧门槛。root2+code5+manifest4共11公开动作，reviewer新增0；无市场payload、来源执行、模型/统计/回测/账户/交易。所有输入指纹见audit.json；actual route UNKNOWN，无自己后台进程。
