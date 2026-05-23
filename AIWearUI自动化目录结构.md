# AIWear UI自动化目录结构

本文档用于指导 UI 自动化项目初始化，技术栈为 `Python + pytest + selenium + YAML + Allure`。  

```text
ui_auto_test/
├── pytest.ini                        # pytest 配置：用例发现规则、标记、命令行参数等
├── requirements.txt                  # 项目依赖清单：pytest、selenium、allure 等
├── conftest.py                       # 全局 fixture 入口：浏览器初始化、公共前后置、失败截图等
├── README.md                         # 项目说明：环境准备、运行方式、目录说明、报告查看方式
│
├── config/                           # 基础配置目录
│   ├── env.yaml                      # 环境配置：baseUrl、浏览器类型、超时时间等
│   ├── account.yaml                  # 测试账号配置：用户名、密码、邮箱等
│   └── logging.yaml                  # 日志配置：日志级别、输出路径、格式等
│
├── data/                             # YAML 测试数据目录，按页面拆分
│   ├── login.yaml                    # 登录页面测试数据
│   ├── edit.yaml                     # 图片编辑页面测试数据
│   ├── merge.yaml                    # 合并图片页面测试数据
│   ├── my_images.yaml                # 我的图片页面测试数据
│   ├── text_search.yaml              # 文搜图页面测试数据
│   ├── image_search.yaml             # 图搜图页面测试数据
│   └── records.yaml                  # 历史记录页面测试数据
│
├── pages/                            # Page Object 层：封装页面行为，减少重复代码
│   ├── base_page.py                  # 页面公共操作：查找、点击、输入、等待、截图等
│   ├── login_page.py                 # 登录页操作封装
│   ├── edit_page.py                  # 图片编辑页操作封装
│   ├── merge_page.py                 # 合并图片页操作封装
│   ├── my_images_page.py             # 我的图片页操作封装
│   ├── text_search_page.py           # 文搜图页操作封装
│   ├── image_search_page.py          # 图搜图页操作封装
│   └── records_page.py               # 历史记录页操作封装
│
├── tests/                            # pytest 用例目录，按页面组织
│   ├── test_login.py                 # 登录页用例
│   ├── test_edit.py                  # 图片编辑页用例
│   ├── test_merge.py                 # 合并图片页用例
│   ├── test_my_images.py             # 我的图片页用例
│   ├── test_text_search.py           # 文搜图页用例
│   ├── test_image_search.py          # 图搜图页用例
│   └── test_records.py               # 历史记录页用例
│
├── utils/                            # 通用工具目录，放简单公共方法
│   ├── driver_utils.py               # 浏览器驱动封装：统一创建和关闭驱动
│   ├── yaml_utils.py                 # YAML 读取工具：加载配置和测试数据
│   ├── log_utils.py                  # 日志工具：输出 info/error 日志并按天归档
│   ├── wait_utils.py                 # 等待工具：显式等待元素状态变化
│   ├── screenshot_utils.py           # 截图工具：失败时按日期保存截图
│   └── redis_utils.py                # Redis 工具：用于读取验证码等前置数据
│
├── logs/                             # 日志根目录
│   ├── info/                         # info 级别日志目录
│   │   ├── 2026-05-09.log            # 2026-05-09 的 info 日志
│   │   └── 2026-05-10.log            # 2026-05-10 的 info 日志
│   └── error/                        # error 级别日志目录
│       ├── 2026-05-09.log            # 2026-05-09 的 error 日志
│       └── 2026-05-10.log            # 2026-05-10 的 error 日志
│
├── report/                           # Allure 报告目录
│   ├── allure-results/               # Allure 原始结果文件
│   └── allure-report/                # Allure 可视化报告
│
├── screenshots/                      # 截图根目录
│   └── failed/                       # 失败截图目录
│       ├── 2026-05-09/               # 2026-05-09 当天所有失败截图
│       │   ├── test_login_001.png    # 登录相关失败截图
│       │   └── test_merge_001.png    # 合并图片相关失败截图
│       └── 2026-05-10/               # 2026-05-10 当天所有失败截图
│           └── test_edit_001.png     # 图片编辑相关失败截图
│
└── test_files/                       # 测试资源文件目录
    ├── images/                       # 测试图片资源：上传、图搜图、合并图片等场景使用
    └── temp/                         # 临时文件目录：运行过程中产生的临时文件
```

## 目录设计说明

1. 当前采用的是小项目简化版结构，不做复杂分层。  
   原因是当前 UI 自动化项目页面数量和用例规模都不大，先保证结构清楚、能快速落地，比一开始搭重型框架更合适。

2. 当前不单独拆定位器 YAML。  
   小项目阶段，页面元素数量有限，定位器先放在 `pages` 层里更直接；等页面明显增多、元素维护成本变高时，再考虑拆分为独立定位器文件。

3. `utils/` 只保留当前明确需要的公共工具。  
   不额外引入复杂设计模式，也不为了未来可能用到的场景预留过多抽象。

4. 日志目录固定按“级别 + 日期”归档。  
   
   - `logs/info/YYYY-MM-DD.log`
   - `logs/error/YYYY-MM-DD.log`

5. 失败截图目录固定按“日期目录”归档。  
   
   - `screenshots/failed/YYYY-MM-DD/`
   - 同一天所有失败截图都放在同一个日期目录下，不再额外按模块二次分层

6. 后续在以下情况出现时，再考虑升级目录结构。  
   
   - 页面数量明显增多  
   - 用例数量明显增长  
   - 多人同时维护  
   - 公共前后置、工具方法、定位器文件开始变得臃肿
