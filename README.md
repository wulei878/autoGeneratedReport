# 自动化生成舆情报告
### 使用步骤
1. 邮箱配置
```py
TEST_MAIL_LIST = config.test_mail_list  # 测试邮箱地址
MAILTO_LIST = config.mailto_list  # 正式邮箱地址
MAIL_HOST = config.mail_host  # 设置服务器
MAIL_USER = config.mail_user  # 用户名
MAIL_PASS = config.mail_pass  # 口令
MAIL_POSTFIX = config.mail_postfix  # 发件箱的后缀
CC_MAIL_LIST = config.cc_mail_list  # 抄送邮箱地址
```
2. 运行
* 测试使用
```py
python scheduleTask.py
```
* 后台自动执行
```py
nohup python scheduleTask.py -t 0 &
```