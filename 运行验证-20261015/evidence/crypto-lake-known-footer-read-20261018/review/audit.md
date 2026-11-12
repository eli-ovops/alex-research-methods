# 已知footer原件有限验收

**PASS_LIMITED_ACTUAL_FOOTER_SCHEMA_METADATA，无必须修正项。**原件支持完成本次metadata-only读取；不是逐行质量、因果数据集或预测/盈利准入。

封存源码/config/scope/gate/单次lock、两HTTP小回执和结果seal一致。精确footer251260648–267304091及header0–3均206，先核Content-Range/长度/ETag/公开version-id再读正文；共16,043,448B。旧tail复用，未重取；本审阅只核4B header为PAR1，不读/重hash/重parse16MBfooter，footer实际SHA通过Owner原始回执与输出seal绑定，不能冒独立全文hash验算。

代码使用真实footer与header/旧tail构造内存BytesIO人工metadata容器，read_metadata成功，容器绝不是完整源文件。未落重复大文件，未解码pages或访问statistics/minmax。输出仅schema及首末各2个组的非价格metadata。声明863,465行、83列、1,728行组；timestamp/receipt_timestamp/sequence_number为INT64且logical_typeNone，双侧20档price/size为DOUBLE，必要字段具备。时钟单位不能由INT64自动确证；nullable是schema声明，不是实际缺失检查。

实际行时钟/范围/顺序/缺口、数量单位、有效报价/状态及历史可得性仍UNKNOWN。contains_gaps仅键名，不能说无gap；created_by Arrow9.0.0只是writer声明，不是生成认证。片段SHA和multipart ETag不冒全文件checksum。旧上限停止结论及hash保持，新单元不是改旧范围后重跑。

执行19.018525833s、采样合并RSS258,523,136B、exit0无活worker，在新范围内；RSS采样非瞬时绝对峰。Owner另计报告与10s检查，Reviewer另保守计2s，计算预算内。Reviewer不受Owner监督器覆盖，无自己后台进程。0新网络、原footer解析、行情pages、来源执行、模型/统计/收益/回测/交易。actual route UNKNOWN。小原件指纹与资源分列见audit.json。
