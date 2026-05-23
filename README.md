# AIWear UI 自动化测试

本仓库用于维护 AIWear Web 端 UI 自动化测试资产，核心项目位于 `AIWear_ui_auto_test/`，技术栈为 `Python + pytest + Selenium + YAML + Allure`。

## 仓库内容

```text
.
├── AIWear_ui_auto_test/              # UI 自动化测试工程
│   ├── config/                       # 环境、账号模板、日志配置
│   ├── data/                         # YAML 测试数据
│   ├── pages/                        # Page Object 页面操作封装
│   ├── tests/                        # pytest 测试用例
│   ├── utils/                        # 驱动、YAML、日志、截图、Redis 等工具
│   ├── images/                       # 测试图片资源
│   ├── report/                       # Allure 结果与报告目录
│   ├── screenshots/                  # 失败截图目录
│   ├── conftest.py                   # 全局 fixture 和失败截图钩子
│   ├── pytest.ini                    # pytest 收集规则、标记和默认运行参数
│   └── requirements.txt              # Python 依赖
├── 页面测试用例/                      # 页面测试用例说明文档
├── AIWearUI自动化目录结构.md          # 项目目录结构说明
└── AIWearUI自动化测试用例思维导图.xmind
```

## 环境准备

1. 进入测试工程目录：

   ```powershell
   cd D:\codes\ChangeClothes\UI自动化测试\AIWear_ui_auto_test
   ```

2. 安装依赖：

   ```powershell
   pip install -r requirements.txt
   ```

3. 准备账号配置：

   ```powershell
   copy config\account.example.yaml config\account.yaml
   ```

4. 按当前测试环境修改 `config/account.yaml` 和 `data/login.yaml` 中的账号、邮箱、密码、预期展示名等占位数据。

## 运行测试

在 `AIWear_ui_auto_test/` 目录下执行：

```powershell
pytest
```

`pytest.ini` 中已配置默认运行参数：

- 测试目录：`tests`
- 用例文件：`test_*.py`
- 默认报告结果目录：`report/allure-results`
- 每次运行前清理旧的 Allure 结果：`--clean-alluredir`

## 查看报告

生成静态 Allure 报告：

```powershell
allure generate report/allure-results -o report/allure-report --clean
```

启动本地 Allure 报告服务：

```powershell
allure serve report/allure-results
```

## 配置说明

- `config/env.yaml`：维护被测环境地址、浏览器类型、超时时间、窗口大小、Redis 配置和测试图片路径。
- `config/account.yaml`：维护本地测试账号信息，由 `config/account.example.yaml` 复制生成，不应提交真实账号数据。
- `data/*.yaml`：维护页面级测试数据，测试用例按业务页面读取对应数据文件。
- `pages/*.py`：封装页面元素定位和页面行为，测试用例通过 Page Object 调用业务操作。
- `tests/*.py`：按页面组织测试用例，包括登录、我的图片、文搜图、图搜图、图片编辑、合并图片和历史记录。

## 注意事项

1. 运行前需确认 AIWear 测试环境可访问，且 `config/env.yaml` 中的 `base_url` 指向正确环境。
2. 邮箱验证码依赖 Redis 读取，需确认 `config/env.yaml` 中 Redis 配置与测试环境一致。
3. 本地浏览器需与 Selenium 驱动能力匹配；当前配置默认使用 Chrome。
4. 失败截图会写入 `screenshots/failed/`，Allure 原始结果会写入 `report/allure-results/`。
