# Known-footer增量静态gate

**PASS_STATIC_ONLY，允许封存输入的一次新known-footer执行。** 本gate没有执行helper或联网；不代表已取得footer、解析成功或真实行质量通过。旧单元ACCEPTED_VALID_CAP_STOP_SCHEMA_UNKNOWN保持原结论，不重跑或改写。

前提已核：旧独立review SHA256 `6c37d8cf9b00baab3e61c6d18da5dc04f9d197c602e9c2da3082910b9c9b07ce`；原8B尾SHA `b23be8d6c7e80a866bdcabed21b4d938f514edfcb2fe1feb14f5a34435324ea8`，PAR1与little-endian footer长度16,043,444相符。旧tail回执为相同ETag/version的206，原始8B而非教学数据。

最终helper SHA `a985f042b604324682bdfe2e3a6e0b4e85c88633dda3300cb426946ac62dbf18`；config `305548424d0ae2e3cad9b4c43adaa04958f47a56593c582e6fcf5c85844c3f81`；scope `e7e4e6eba8c358e6fb21de379f9063ade5e3156afc88d9d77f831922e1d9c8c4`。gate.json完整绑定source-seal全部6项，包括旧review、旧依赖健康回执与tail。

- helper:60–65只本地读取既存8B，明确声明必须等于16,043,444。实际新范围仅footer `251260648–267304091` 与header `0–3`，2请求共16,043,448B；不重新请求尾8B。
- helper:33–58保留空ProxyHandler、NoRedirect、精确URL的匿名Range+If-Match；先核206、Content-Range/Length、ETag、version，再read；累计body上限固定且无重试/其他地址。
- helper:9–16、50–53在JSON/二进制写入前检查32MiB预算；69–70只以BytesIO在内存构造明确人工metadata-only容器，不再落地第二份16MBwrapper；数据页不存在且不读。
- helper:71–81仅输出schema/types/声明计数；rowgroup最多首2与末2，不调用statistics/minmax、价格、data-page读取或模型。输出摘要仍受JSON预写容量检查。
- helper:87–101核封存与gate、建立新目录exclusive formal-started.lock，沿原venv解释器启动隔离worker；107–114用512MiB RSS采样监督、CPU/IO设置2、300s及14:12:55Z截止，超限终止不扩资源。RSS为100ms采样，不是绝对瞬时硬限。

已有PyArrow26依赖preflight来自上一单元，本轮只核其原件身份，不重跑依赖或扩大解析实验。本次AST仅语法静态parse，不执行来源/Owner helper。正式运行仍须核真实2响应、身份、总bytes、parser结果、32MiB disk/采样RSS/elapsed与worker退出；任何失败停止，不把资源边界停止写成数据损坏或成功。

运行结果最多证明footer声明；不证明真实时间范围、逐行连续性、完整文件hash、信号/收益或容量。actual route UNKNOWN；0本review公网/GET、helper执行、模型/统计/回测/交易。仅本preflight-review两报告保留，无清理项。
