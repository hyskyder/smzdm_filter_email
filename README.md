# smzdm_filter_email
过滤什么值得买(SMZDM)优惠信息，发送邮件给指定邮箱。

# 调用
1. 准备config.ini
2. python smzdm.py

# 配置文件 config.ini
``` ini
[email]
#脚本将向此邮箱发送邮件:
mailto=your@email.address 
#邮件标题:
subject=SMZDM今日
#目前只支持通过mailgun服务发送邮件:
mode=mailgun

# mailgun mode
mail_from=postmaster@sandbox3456353438(*your_email*)17236bc196da.mailgun.org
mailgun_domain=sandbox3456353438(*your_domain*)17236bc196da.mailgun.org
mailgun_apikey=key-3462456367(*your_key*)3675637456746


# 感兴趣的物品将会在邮件中置顶
[interests]
MyInterets=你感兴趣的关键字A|关键字B

[filter]
任意类别A=任意关键字1|关键字2|关键字3|....
任意类别B=任意关键字a|关键字b|关键字c|....
#[filter]下的任何关键字都将成为过滤字符串. '类别'仅为用户分类方便.

[mallfilter]
我不想看到这些商家平台=平台1|平台2|


[advance]
#脚本一次执行最多从什么值得买取得几条优惠信息:
max_num_get=200
#是否在邮件末尾附上运行LOG:
append_log=1
#运行LOG的详细程度 
verbose=2

```

依赖：
* requests (pip install requests)