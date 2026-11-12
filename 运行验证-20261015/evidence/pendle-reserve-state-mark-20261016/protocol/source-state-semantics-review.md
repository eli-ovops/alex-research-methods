# Pair持久储备状态语义：静态审阅

限定PASS：**若该地址实际runtime符合所读声明源码，且固定端点前实际Sync返回完整，最后一条Sync可支持stored reserve0/1的持久状态层。** 不能称freshquote、可成交出售价格或净盈利。0网络/源码执行/编译/EVM/模型/回测/交易；不读新价格、不计算新profit。

固定scope SHA1442e729199b0143a025c1f5d3e8b4327314e00b14a9fa1e705c8549fb6b5799已核，原seed入场block16857476/log186，端点为兑回前完整block16940286。须保留同seed区块内后续更新，以block/globalLog排序；未来分页/去重/时间/字段审阅由根原件另核，本报告不先宣称取得完整事件。

## reserve写路径

所读Pair主源共201行，private reserve0/1正常显式赋值仅82/83，两者和blockTimestampLast写在_update，紧接85emitSync。mint在LP铸造及读取balances后128调用，随后emitMint；burn在烧LP、转底层、重新读balances后153调用，随后emitBurn；swap在输出转账/可选callback/读取余额/输入量与K检查后185调用，随后emitSwap；sync直接以当前balances在199调用，即使储备数值不变仍可emitSync。失败交易状态和日志回滚，不能把失败尝试当持久写。

skim只转超出储备的余额，未写reserve/emitSync；直接捐币/转账/代币rebase也可改变余额而不改stored reserves，直到下次_update相关路径。无新Sync可意味着**储备状态持续**，不意味着币价仍新鲜、余额等于储备或可按ratio成交。Pair无owner/pause路径，lock是同交易重入保护；不证明外部token无暂停/拒绝转账。继承ERC20的assembly仅取chainid，未见delegatecall/sstore或绕过reserve赋值路径。仅源码语义，未独立编译验证runtime。

## 入场token顺序与精度

入场收据成功、Pair唯一Sync log186与Swap log187。Swap四原量为amount0In34938561458835930、amount1In0、amount0Out0、amount1Out389881219915010885407。原WETH实际入Pair transfer(log184)与amount0In同量，LOOKS实际由Pair转出(log185)与amount1Out同量，结合源码事件语义支持**当笔token0=WETH/token1=LOOKS**，不是独立runtime getter或部署storage证明。

Pair initialize仅factory可调，注释calledonce但函数无显式一次性检查；factory源码未读。不把token顺序擅称immutable，也不猜实际曾重初始化；此为跨期identity的明确条件，非否定当笔证据。所读provider Proxy0/源码声明不替代独立字节码身份。

LOOKS provider源继承ERC20decimals返回18、LooksRareToken未覆盖；WETH复用旧AMM `WETH9.sol`声明uint8 public decimals=18，均已有本地原件指纹。**Pair的LPdecimals18不能代替底层币精度证据**。无新GET/runtime调用。

完整实际Sync可补“固定端点stored状态”，不能改旧100块无freshSync为有freshquote。ratio估值、ETH-WETH平价、slippage和最终费用净额须另行明确，本轮未算。所有实际输入SHA与源码行号/ABI/原量见JSON。审阅UTC：2026-10-16T10:24:13.869663+00:00；实际model/effort UNKNOWN，未改他人文件。

JSON SHA256：`8efd8e9cc958a185bb3c40a1858a7bc80af0820a064fc4f88e175b07527ff472`。
