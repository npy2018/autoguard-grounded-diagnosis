# AutoGuard Grounded Diagnosis

一个**受工具和证据约束的自动驾驶根因诊断Agent**。它不允许大模型只凭上下文“讲故事”：所有结论必须来自内部API查询结果，并绑定可解析证据URI。

## 核心方法

- ReAct式“调用工具获取事实”，但不暴露或依赖自由漫游式思维链；
- 只读SQLite证据库，提供日志、版本Diff、回放和历史案例工具；
- 最大步骤数，防止Agent死循环；
- 每个根因必须包含支持证据、反证、缺失信息、可证伪预测和实验；
- 无足够证据时强制输出`insufficient_evidence`；
- 可选OpenAI-compatible结构化输出后端，默认Demo完全离线。

## 快速运行

```bash
pip install -e '.[dev]'
python scripts/run_demo.py
uvicorn app:app --reload
```

## 证据URI示例

```text
log://EVT-001?t=12.34&signal=object_328.class
version://V2.7.0/change/CFG-108
replay://EVT-001/V2.6.8?t=12.34&field=object_328.class
case://CASE-17
```

## 生产接入

将`EvidenceStore`替换为企业日志湖、代码库、缺陷库和视频索引；工具接口与Pydantic输出契约保持不变。可选DuckDB适合直接查询Parquet，但核心实现使用标准SQLite以保证开箱即用。

详见 [SOURCES.md](SOURCES.md)。
