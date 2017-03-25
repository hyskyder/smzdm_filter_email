# smzdm_filter_email
过滤什么值得买(SMZDM)优惠信息，发送邮件给指定邮箱。

![效果](https://lh3.googleusercontent.com/GAMvDOSXw9ca8S03oC-wPHsI38H8pis6Fu6SiXrmS0KtveOGBiBVCPkpfhIwpksFg0trDcned4e7ExDkTxMF4OcDYkGuUJkcNfhPUuusYuXJ9qkZoAHc6lOSd7_V6Znod1R4yGchEi4r7s3q5RHZ_HxyqAvxvff-1tuy_Gd1fm4AcpXCypcfkfeavduFH7U-UiMQOuc7Uh9u1lvm4BsLdfsHIdu94b01OQLFXs8QYdLAV9NKUC831Kf-Uorj89ogY-EEZOF3FjQea07ND5BJgJ7Y4Zc8qOLqXcFOQ2wBiwJAYMtZBJmTglWhXEFJEl-JapxpFxoCPl4NRy88j_FlrN_LHcarfyuJDneXDrPX6lbGDEdTlHW-9oCqtWRJIbJYoBusPjt-va3t9POaCVoBrYEhzB-CjBoqOLaxEebeNjZNd_TNVica_jUBAcYF3MyuFSmJJaflXT75UGsTkNjVBIzwBTGKQMVBDjiyg-A3_rJa56J6ZeiG6DbVnW4_lrQo3QGmCkO9McoG04VK3YohOByOXq4O5-n7JXbVUkz9Efl8GMN446bHcZ4XgddIocggeNQjwqFS466txK2U3ad-2ELZIvaVKwfpBokgIG0T2GdLgc4IlDa4=w600-no "效果图")

# 调用
1. 准备config.ini
2. python smzdm.py

# 配置文件 config.ini
``` ini
[email]
#脚本将以此邮箱的身份发送邮件:
mailto=your@emial.address 
#邮件标题:
subject=SMZDM今日
#暂时只支持通过mailgun服务发送邮件:
mode=mailgun

# mailgun mode
mail_from=postmaster@sandbox3456353438(*your_email*)17236bc196da.mailgun.org
mailgun_domain=sandbox3456353438(*your_domain*)17236bc196da.mailgun.org
mailgun_apikey=key-3462456367(*your_key*)3675637456746

[filter]
任意类别=任意关键字1|关键字2|关键字3|....
任意类别=任意关键字a|关键字b|关键字c|....
#[filter]下的任何关键字都将成为过滤字符串. '类别'仅作为用户分类方便设置.

[advance]
#脚本一次执行最多从什么值得买取得几条优惠信息:
max_num_get=180
#是否在邮件末尾附上运行LOG:
append_log=1

```

已测试平台：
* python 2.7.6 (ubuntu)
* python 2.7.13 (windows)

依赖：
* requests (pip install requests)