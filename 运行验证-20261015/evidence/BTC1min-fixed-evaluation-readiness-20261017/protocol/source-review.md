# 既有依赖与小模型方案的有限准入

结论：可以保留**无需新增依赖的透明改编候选**，尚未证明环境实际可运行。只用了系统 python3 -S 与标准库读取指定项目的 dist-info、pyvenv.cfg 和硬件资源；没有激活或启动项目虚拟环境，没有导入科学/模型包、安装、实现或运行模型。

项目环境元数据是 CPython3.12.14、Torch2.8.0、NumPy2.2.6、pandas2.2.2、SciPy1.18.1。没有检出 scikit-learn、TensorFlow、Keras；指定项目根目录的6种常见锁文件也未见。元数据存在不保证二进制依赖、导入或实际计算健康。

设备为 arm64 macOS、10逻辑CPU、16GiB物理内存；项目卷可用空间约1.789TB，精确瞬时字节见 runtime-evidence.json。物理内存不是当前空闲或已预留内存；未查看用户进程或账户。没有测速，不能保证未来预算内完成。

有限路线是：Torch单层、单向、无dropout的 LSTM，输入3维、隐藏16维，batch_first=True、bias=True、proj_size=0；取最后时间步，经 Linear(16,1)。窗口独立的初始隐状态/单元状态拟设零，CPU、float32、种子20261017、6线程均仅是拟固定设置。它是新框架下的透明改编，不是作者2021年Keras输出的精确复现。

PyTorch2.8官方Adam页明确默认lr0.001、betas(0.9,0.999)、eps1e-8、weight_decay0和amsgrad=False。foreach/fused的默认是None；为减少实现选择差异，方案可显式设False，不能将其称默认。LSTM官方页给出权重与偏置均匀初始化范围；固定种子不保证不同版本、平台和BLAS结果相同。Linear头的初始化未在这三份文档内另核，不冒历史Keras等价。

由于sklearn未安装，线性对照候选可以用现有NumPy明确求Ridge正则化方程，alpha=1、仅训练集中心化、截距不惩罚，并以float64求解；使用相同扁平化窗口和同一批时点。NumPy2.2官方solve页支持方阵满秩求解，奇异或非方阵会报错。这不是已经安装的sklearn Ridge，也没有实现或求解任何实际矩阵；若未来数值失败应记停止，不能静默换参数或求解器。

本轮3份版本对应官方文档、4次逻辑open、2次native调用；额外一次仅定向补第三份NumPy同页正文，首复合返回只有标题，未增加第四来源。保存的是原生工具抽取，不冒HTTP原始正文/请求头；独立发布日期及精确逐次HTTP时间UNKNOWN。具体URL、正文行定位、参数、输入SHA256和字节见 source-review.json 与官方快照。

唯一决策影响：根可用这些元数据和API语义冻结一次有限、可审阅的后续方案，无需现在安装TF/sklearn；运行健康、时间/内存实测和执行授权仍未核。本轮模型训练、预测、评分、回测、模拟、交易、行情获取均0。actual model/effort UNKNOWN，目标未实现。
