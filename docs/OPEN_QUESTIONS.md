# OPEN QUESTIONS

## OQ-001 (2026-11-04) — AGENTS.md V6 命令路径与 uv 工作目录不一致

- **现象**：AGENTS.md「验证协议」V6 写作 `uv run pytest backend/tests/test_tenant_isolation.py -x`，但 V1–V3 约定在 `backend/` 目录下执行，而 uv 项目（`pyproject.toml`）位于 `backend/`，仓库根目录没有 uv 项目。按字面执行：在根目录 `uv run` 找不到项目；在 `backend/` 下路径 `backend/tests/...` 不存在。
- **当前可用的等效命令**：在 `backend/` 下执行 `uv run pytest tests/test_tenant_isolation.py -x`；或在仓库根目录执行 `uv run --directory backend pytest tests/test_tenant_isolation.py -x`。
- **另**：V6 需要 pytest 配置（`DJANGO_SETTINGS_MODULE`），已在 `backend/pyproject.toml` 增加 `[tool.pytest.ini_options]`。AGENTS.md「已知残缺与坑」中"pytest 无配置文件"的描述已过时。
- **待裁决**：由人工更新 AGENTS.md 的 V6 命令与上述描述。
- **✅ 已解决（2026-11-04，经用户指令）**：AGENTS.md V6 改为在 `backend/` 下执行 `uv run pytest tests/test_tenant_isolation.py -x`（注释给出仓库根目录等效命令），与 V1–V3 的工作目录约定一致；「已知残缺与坑」中 pytest 条目改为记录现行配置；CLAUDE.md 同步更新。两种写法均已实测通过。
