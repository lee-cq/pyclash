# 自定义Clash文件合并

## 目录结构

/pyclash/   pyclash源码

/pyclash/apis  FastAPI目录

/pyclash/config/  pyclash 配置文件目录

/pyclash/tools.py   工具集

/pyclash/common.py   pyclash公共标识

/pyclash/app.py   fastapi 启动文件

/config/  clash_core 配置文件目录  工作目录

/config/ruleset/  clash规则集存放目录

/tests/     pyclash 单元测试


/makefile  构建脚本 IF Linux

/bootstart.sh   启动脚本

## API

1. 代理：

   1. 列出全部走代理的规则
   2. 添加一条走代理的规则
   3. 删除一条走代理的规则
2. 直连规则

   1. 列出全部的直连规则
   2. 添加一条直连的规则
   3. 删除一条直连的规则
3. 规则提供商

   1. 列出全部的规则提供商
   2. 列出指定的代理提供商
   3. 新建规则提供商
   4. 更新规则提供商
   5. 删除规则提供商
4. 代理提供商

   1. 列出全部的代理提供商
   2. 列出指定的代理提供商
   3. 新建一个代理提供商
   4. 更新一个指定的代理提供商
   5. 删除一个代理提供商
5. 代理组

   1. 列出代理组
   2. 列出指定的代理组
   3. 新增一个代理组
   4. 更新一个代理组
   5. 删除一个代理组
6. 隧道

   1. 列出全部的隧道
   2. 新增一个隧道
   3. 更新一个隧道
   4. 删除一个隧道

## Classical Type

```yaml
rules:
  - DOMAIN-SUFFIX,google.com,auto
  - DOMAIN-KEYWORD,google,auto
  - DOMAIN,ad.com,REJECT
  - SRC-IP-CIDR,192.168.1.201/32,DIRECT
  - IP-CIDR,127.0.0.0/8,DIRECT
  - IP-CIDR6,2620:0:2d0:200::7/32,auto
  - GEOIP,CN,DIRECT
  - DST-PORT,80,DIRECT
  - SRC-PORT,7777,DIRECT
  - MATCH,auto
```
