# precooling-study

预冷批次分段交接、售后重量和经济账核对。

## 当前产品

这是可独立运行的本地分析应用，提供业务记录核对和确定性基线结果。各业务职责可直接作为 Python 接口调用，`app.py` 负责组合一次只读业务检查。结果可保存为 JSON，不依赖远端服务。

- `transfers.py`：分段交接和共用称重的可见记录。
- `outcomes.py`：售后损耗及销售终点口径。
- `economics.py`：农户收益、扣款和财政成本。

## 运行

使用 Python 3.11.14，无需安装第三方包。

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q .
python3 app.py demo
```

`inspect` 与 `demo` 使用相同业务入口；`--as-of` 选择已知日期，`--data` 可选本地数据文件，`--output` 可将本次业务核对结果写入文件。默认数据位于 `fixtures/data.json`，默认日期为 `2026-11-01`。这些命令仅展示当前已经存在的能力。

## 容器

`Dockerfile` 固定到 Python 基础镜像内容摘要。构建后运行不联网：

```bash
docker build -t precooling-study:local .
docker run --rm --network none precooling-study:local python -m unittest discover -s tests -v
docker run --rm --network none precooling-study:local
```

## 数据与业务契约

样例记录全部为本地合成数据，不代表真实农户、市场成交或实际试验结果。日期采用 `YYYY-MM-DD`，有记录时点的条目以 `recorded_at` 表示系统已知日期；同一业务键存在多个修订时选已知范围内最新记录，同日由 `revision` 区分，`withdrawn` 表示撤回。可修改样例验证业务边界，不能将演示数据的统计方向视为真实结论。

报名以enrolled_on判断在指定批次发运时是否有效，precooled记录实际处理，两者不同。未回访损耗为null。财务同时保留农户净收益和财政补贴支出，成本版本可选择；基线只作描述与实账核对，不将组均值差称为处理效果。 transfers记录分段称重区间；batch_shares是同次称重的账面分配份额，不是各批真实重量的独立测量。相同校准组保留共同偏差信息。observed_balances只列账面分配，不将差额解释为损耗。paid_records是已付款事实，不能被分析重写。

接口细节见 `docs/contracts.md`。测试使用各自的内存副本和临时目录，不修改原始数据或依赖固定端口。
