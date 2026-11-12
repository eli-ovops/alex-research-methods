# NumerAPI公共逐轮记录入口

限定完成：4次官方文档／源码读取已用完，没有请求任何模型记录。原生返回及各返回字节／SHA保存在同名JSON；这是工具抽取，不是HTTP原件。文档标识3.1.1，索引列版本日期2026-08-12；Git commit及精确页面发布日期UNKNOWN。

## 已明确的公共身份链

[官方客户端文档](https://numerapi.readthedocs.io/en/latest/) → [API参考](https://numerapi.readthedocs.io/en/latest/api/numerapi.base_api.html) → [直接链接的base_api源码](https://numerapi.readthedocs.io/en/latest/_modules/numerapi/base_api.html)。未取得对应GitHub仓库／commit，不猜写。

源码L19给公共GraphQL endpoint `https://api-tournament.numer.ai`；L461–475的`public_user_profile`以`model_name:String!`和`tournament:Int`查询`v3UserProfile`，返回`id/startDate/username/bio/nmrStaked`。L432–435说明`id`是该赛道model UUID。调用没有`authorization=True`，默认匿名构造见L89–156；这是客户端设计，尚未验证服务器实际返回。首页L106列Classic赛道8。可用NB_EXAMPLE_MODEL作目标名，实际存在性及UUID尚未由本轮取得。

## 逐轮记录与实际到账不能混用

API参考标记两个旧逐轮performance方法弃用，建议`submission_scores`。可见v2描述含round编号／时间／resolved、atRisk、payout配置及pending／settled分项；daily方法主要给信誉／排名序列，不等于完整现金账。[包参考](https://numerapi.readthedocs.io/en/latest/api/numerapi.html)

本次source返回仅到L857，未包含后半逐轮方法实现；不提供猜测的逐轮GraphQL或分页／日期过滤。根后续定向补读不计成本子任务已读原件。`pending_model_payouts`文档明确针对已认证用户，不是公共username接口，不调用。

尚无本轮实际逐轮stake、burn、payout到账、transaction hash、gas或美元全费记录；原提交向量、固定权重与示例版本绑定亦未取得。字段名不能证明实际到账或个人净盈利。认证账户／提交方法不当作公共替代。

状态`PASS_LIMITED_CLIENT_DOCUMENTATION_QUERY_CHAIN_PARTIAL`。实际model/effort UNKNOWN。读取4次、API数据请求0、安装／导入／凭证／账户／提交／质押／模型／回测／交易均0。停网停止，剩余精确公共记录核验归根Owner。
