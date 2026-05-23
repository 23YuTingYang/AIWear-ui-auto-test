# AIWear Web UI 自动化

基于 `Python + pytest + selenium + YAML + Allure` 的 Web UI 自动化项目。

## 运行方式

1. 安装依赖：`pip install -r requirements.txt`
2. 复制账号配置模板：`copy config\account.example.yaml config\account.yaml`
3. 修改 `config/account.yaml` 和 `data/login.yaml` 中的占位账号数据
4. 执行测试：`pytest`
5. 生成 Allure 报告
   - `allure generate report/allure-results -o report/allure-report --clean`
   - `allure serve report/allure-results`

## 说明

1. 测试环境地址、浏览器和超时时间读取 `config/env.yaml`
2. 测试账号读取 `config/account.yaml`，该文件不提交到代码仓库
3. 邮箱验证码通过 Redis 读取，Redis 配置同样在 `config/env.yaml`
4. 仓库中的 `data/login.yaml` 使用占位账号数据，运行前需要替换为当前测试环境可用的账号、邮箱和期望显示名称
5. 测试图片读取 `config/env.yaml` 中 `paths` 配置的本地图片路径
