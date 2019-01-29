---
layout: post
title: Jacman主题网站自定义过程
date: 2018-06-28 23:18
tags:
- other
categories: other
description: 觉得原先的主题太丑，自定义的范围太小，决心自己学习前端知识并修改主题代码
---

### 如何设置 Header 的背景

学习方法：检查元素 + CSS school 测试 + Google + Jekyll 本地运行

先阅读各种布局的html，定位到控制样式的style.css，分别作如下修改：

-  将loge_me 修改成圆形：

  ```css
  #imglogo img
  {
      width: 4em;
      border-radius:50%;
  }
  
  @media only screen and (min-width:768px)
  {
      #imglogo img
      {
          width: 5em;
          border-radius:50%;
      }
  }
  
  @media only screen and (min-width:1024px)
  {
      #imglogo img
      {
          width: 5.5em;
          border-radius:50%;
      }
  }
  
  ```

- 添加背景图片，header的

  ```
  body >header
  {
      width: 100%;
      -webkit-box-shadow: 2px 4px 5px rgba(3,3,3,0.2);
      box-shadow: 2px 4px 5px rgba(71,100,244,0.2);
      background: url("/assets/img/your-name.jpg") no-repeat fixed center;
      background-size: cover;
      color: #fff;
      padding: 1em 0 .8em;
  }
  ```

  