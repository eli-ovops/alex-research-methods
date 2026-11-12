# 单份ETH期权报价输入包独审

**PASS_LIMITED，material_errors=[]。** 独立从830条实际instrument元数据筛得77个合格call，最近合格周五2026-10-23 08:00 UTC共有20个候选，以预先规则和独立index2419.91选中2400执行价。报价前锁定23:59:38.125297 UTC，book时间23:59:44.631 UTC；未按bid、mark或收益挑合约。

合约`ETH-23OCT26-2400-C`实际字段：ETH报价、ETH保证金／最终结算、contract_size=1、min_trade_amount=1。counter_currency=USD不是期权权利金币种；lot_size=10不能替换明确的最小交易数量。此价区间的tick_size_steps为0.0005，bid/ask均合步长。

原book买价0.0265、卖价0.0275 ETH，显示数量386／454；last0.021、mark0.0269、settlement0.035912不能替换两边报价。bid/ask IV41.35／43.29、mark IV42.04是平台衍生字段，不是本次独立定价结果。underlying2422.12对应`ETH-23OCT26`远期／期货，不能和bookindex2419.87互换。选取index与book相隔102.565264秒，不是同一时刻的矛盾数值。

三份实际HTTP原件均与成功回执SHA／bytes一致，生产testnet=false。普通commission=0.0003与官方Standard费用定义相合；上限、实际账户档位、交割及其他成本仍须具体应用，未发生订单或真实收费。数据条款与个人资格限制继续保留。

这份原件只支持一次公开输入的字段、时间和单位对应；depth1不证明保证成交、持续流动性、可用容量、保证金充足或盈利。不计算期权公允价、不复现IV或模拟交易。16项实际读取输入绝对路径／SHA256／bytes及完整观察值见JSON。新增网络、来源／SDK／SQL／EVM／模型／回测／交易执行均0；actual model/effort UNKNOWN。
