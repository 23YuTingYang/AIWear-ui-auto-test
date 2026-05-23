# AIWear Web UI 自动化

基于 `Python + pytest + selenium + YAML + Allure` 的 Web UI 自动化项目。

## 运行方式

1. 安装依赖：`pip install -r requirements.txt`
2. 执行测试：`pytest`
3. 生成 Allure 报告
   - `allure generate report/allure-results -o report/allure-report --clean`
   - `allure serve report/allure-results`

## 说明

1. 测试环境地址、浏览器和超时时间读取 `config/env.yaml`
2. 测试账号读取 `config/account.yaml`
3. 邮箱验证码通过 Redis 读取，Redis 配置同样在 `config/env.yaml`
4. 测试图片默认复用 `接口自动化测试/api_auto_test/testdata/images`
