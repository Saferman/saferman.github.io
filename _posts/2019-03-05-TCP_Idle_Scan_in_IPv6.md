---
layout: post
title: TCP Idle Scan in IPv6 原理研究
date: 2019-03-05 11:40
tags:
- research
- scan
categories: research
description: 研究一下 TCP Idle Scan 技术能否在 IPv6 中实现
---
这是我在段海新老师的课程上想到的一篇文章。虽然之前注意过 Idle Scan，但是一直没有很在意这种空扫描的技术原理是如何实现的。今天我就想探究一下 Idle Scan 的原理，并且搞清楚这种空扫描技术在 IPv6 的网络中能否实现以及如果可以实现和 IPv4 的空扫描有什么区别。因为我写这篇文章的时候还没有中文相关的资料，我只有参考最早的论文《TCP Idle Scans in IPv6》。

那篇论文涉及的 RFC 在今天都有所更新，因此本篇文章提供的方法是否仍然可行还在我的研究计划中，我也会尝试探索新的 RFC 规定会不会引发新的安全问题。之后会用 Python 实现一个 TCP Idle Scan in IPv6 的工具。

需要掌握的先验知识：

- IPv4 报头组成，尤其是 Identification 字段
- TCP 握手的三步骤以及非预期的处理

### 先验知识

IPv4 的报头总共有 20 字节的固定部分，其中有一个 4 字节标识字段 (Identification)，该字段的作用如下：

> 该字段和 Flags 和 Fragment Offest 字段联合使用，对较大的上层数据包进行分段（fragment）操作。IP 软件在存储器中维持一个计数器，每产生一个数据报，计数器就加 1，并将此值赋给标识字段。但这个“标识”并不是序号， 因为 IP 是无连接的服务，数据报不存在按序接收的问题。 当数据报由于长度超过网络 的 MTU 而必须分片时， 这个标识字段的值就被复制到所有的数据报的标识字段中。 相同的标识字段的值使分片后的各数据报片最后能正确地重装成为原来 的数据报。

下图展示了 TCP 连接的三种状态，对应不同的三种状态：成功建立 TCP、拒绝建立 TCP 以及非预期的数据包。

![图 1](https://saferman.github.io/assets/img/idle_scan_in_ipv6/tcp_three_way_shakehand.png)

### TCP Idle Scan in IPv4

下图非常清晰的展示了 IPv4 的 Idle Scan 步骤和原理，这种空扫描能成功执行的一个核心的原因是 Idle host 的 Identification 的实现是通过全局变量控制的。

![图 2](https://saferman.github.io/assets/img/idle_scan_in_ipv6/TCP_Idle_Scan_in_IPv4.png)

这部分我就不做详细的步骤说明了，主要是第四步如果端口开放了会返回 4b SYN/ACK 数据包，这样 Idle host 会发送一个 RST 给 Target 并让 IPID+1；如果端口未开放或者过滤 Idle host 会收到 4a.RST 就不会继续发送 RST 了。这样攻击者只需要在第七步根据 IPID 的数值判断 Target 对应端口是否是开放的。

### IPv4 和 IPv6 的报头对比

我觉得这张图是做的真的好，非常清晰，基本看图就明白了。

![图 3](https://saferman.github.io/assets/img/idle_scan_in_ipv6/ipv4_vs_ipv6.png)

可以看到在 IPv6 的包头中并没有 Identification 字段了。但是 IPv6 有拓展报头（位于 IPv6 头部和 TCP 头部之间），当 IPv6 数据包分片的时候会使用拓展报头，在拓展报头里存在 Identification 字段。

因此要想在 IPv6 的网络中利用基于 Identification 的 Idle Scan，需要先想办法让 IPv6 数据包分片。

### IPv4 分片 vs IPv6 分片

在 IPv4 中，主机和路由节点都可以进行分片，但是在 IPv6 中，只有主机节点才能分片，中间的节点不能进行数据包分片。IPv4 分片和 IPv6 分片对比如下：

![图 4](https://saferman.github.io/assets/img/idle_scan_in_ipv6/ipv4_fragment_vs_ipv6_fragment.png)

可见 IPv6 的数据包如果过大，中间节点会返回一个 ICMPv6 Packet Too Big 消息通知主机需要分片 IPv6 地址，然后由主机分片数据包，中间节点会将分片的数据包原封不动的转发。

接下来我们看看在 TCP Idle Scan in IPv4 的原理图中哪些部分涉及到 IPID 字段：

![图 5](https://saferman.github.io/assets/img/idle_scan_in_ipv6/ipv4_IPID.png)

图中红线的部分就是需要 IPID 字段的步骤，因此在 IPv6 中我们需要在红色这几个步骤传输携带 Identification 标识的 IPv6 数据包。

### TCP Idle Scan in IPv6

要想第二步和第七步的服务器响应 IPv6 数据包分片其实并不难，遵循 RFC 规定：

> If the Request is fragmented, the Reply will be fragmented too
>
> The data received in the ICMPv6 Echo Request message
> MUST be returned entirely and unmodied in the ICMPv6
> Echo Reply message. (RFC 4443, ICMPv6)

这样 attacker 和 Idle host 主机之间的通信就变成下图：

![图 6](https://saferman.github.io/assets/img/idle_scan_in_ipv6/IPv6_fragment.png)

FH 全称 fragment header，是拓展头中关于分片部分的头字段，这样就携带了 IPID 信息。现在剩下的问题就是如何将 Idle host 和 Target 之间的通信进行分片（红色第五步），这里需要参考 RFC 1981, Path MTU Discovery for IP version 6：

> When a node receives a Packet Too Big message, it MUST
> reduce its estimate of the PMTU for the relevant path, based on
> the value of the MTU eld in the message
> A node MUST NOT reduce its estimate of the Path MTU below
> the IPv6 minimum link MTU. Note: A node may receive a
> Packet Too Big message reporting a next-hop MTU that is less
> than the IPv6 minimum link MTU. In that case, the node is not
> required to reduce the size of subsequent packets sent on the
> path to less than the IPv6 minimum link MTU, but rather must
> include a Fragment header in those packets

简而言之就是如果一个节点收到与之通信的节点返回的 Packet Too Big 消息，这个节点就需要根据消息中携带的 MTU 重新计算相关路径的 PMTU 值，特别的如果消息告知的 MTU 小于最小的 IPv6 链路传输大小，节点不用实际之后的 IPv6 数据包分片，但是必须要携带 fragment 拓展头字段，这样就携带了 IPID 信息。

因此在上一张图片的第一步前面我们需要加上几步来达到让 Idle host 和 Target 传输数据包需要分片的操作，最终的原理图如下：

![图 7](https://saferman.github.io/assets/img/idle_scan_in_ipv6/TCP_Idle_Scan_in_IPv6.png)

我将按照顺序讲解每一个步骤发生的事情：

1. 首先，攻击者向 Idle host 发送一个源地址伪造成 Target 的 ICMPv6 Echo Request，这会导致 Idle host 响应给 Target。此 Echo 请求包含足够的数据以致于响应的请求也需要分片，因此 Idle host 将在其响应中使用扩展头进行分段（FH）。这个环节涉及的 FH 中的 ID 字段与整个攻击无关。
2. Idle host 将使用 ICMPv6 Echo Response 应答给 Target，此响应包含请求中收到的所有数据，因此也需要进行分段。此消息中扩展标头（FH）中的 ID 标识值与整个攻击无关。
3. 尽管 Target 接收到 ICMPv6 Echo Response，但是 Target 不会响应 Idle host。相反，攻击者可以继续发送一个源地址伪造成 Target 的 ICMPv6 Packet Too Big message，并且携带的 MTU 信息小于最小 IPv6 MTU 值。当 Idle host 收到这个消息后，会给所有发送给 Target 的 IPv6 数据包添加拓展头用于分片，即使某次发送的 IPv6 数据包无需分片。
4. 与 TCP Idle Scan in IPv5 类似，接下来的两个步骤的目的是获取 Idle host 当前在分片中使用的 ID 值大小。为此，攻击者向 Idle host 发送 ICMPv6 Echo 请求，该请求包含需要分片的足够数据。攻击者使用的扩展标头中的标识值与整个攻击无关。
5. 在收到 ICMPv6 Echo Request 后，Idle host 将回复 ICMPv6 Echo Response，其中包含 ICMPv6 Echo Request 中收到的所有数据，因此也会被分段。攻击者获取存储在扩展头中的 IPID 值。
6. 后面的步骤就和 TCP Idle Scan in IPv4 一样了

至此完成了 IPv6 中的 TCP Idle Scan。要想成功利用这个扫描技术，同样需要 Idle host 具有全局的 ID 计数器，我阅读的论文中作者调研了各个系统的 Identification 分配策略如下：

![图 8](https://saferman.github.io/assets/img/idle_scan_in_ipv6/assignment_of_identification.png)

Windows 是使用的全局 Identification 计数器，喵 ~

### More

RFC 4443 文档已经被 4884 更新了，之后再 2018 年又被 8335 更新

RFC 1981 文档也被在 2017 年被 8201 更新

那么是否本文提到的方法还仍然适用值得后面进一步研究