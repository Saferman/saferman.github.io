---
title: PHP Source Research for CTF
date: 2018-10-19 10:58
tags:
- CTF
- Web
- PHP
categories: CTF
description: 为了更加全面的吃透 PHP 特性，我决定更加深入的研究 PHP 常见函数底层代码实现
---

作为一名不擅长开发 PHP 的 CTFer，近期从各大 CTF 的 PHP 源码审计收获了很多，比如 hacklu 比赛以及最近的研究的 [php 代码审计分段讲解](https://github.com/bowu678/php_bugs) 项目。虽然通过专注的解题最终能够解决这类题目的，但是通常需要花费很多时间在查阅文献和测试上面。相信有很多 CTF 选手对此也是深有体会。

究其根本原理，我们在看到一个 PHP 函数的时候，很难准确快速的说出和这个函数的全部特性（哪些字符可以绕过，怎么处理非预期的数据类型等等）。比如第一次接触下面的这段判断语句，你能快速告诉我怎么才能让 if 里的判断语句为假吗？

```php
if($req['number']!=strval(intval($req['number']))) {
     $info = "You are stupid!";
}else{
     $info = "You are clever!";
}
echo $info;
```

又或者今年的 hacklu 一段代码，if 里的判断逻辑怎么才能为 True？第一次接触这类问题，你花了多少时间想到？

```
$cc = 1337;$bb = 42;
@$cc = $_GET['cc'];
if(substr($cc, $bb) === sha1($cc)){
    ......
}
```

还有如果 $bb 可控，为什么下述代码会出现恶意代买执行漏洞？

```php
assert("$bb == $cc");
```



所以很有必要详细阅读一遍 PHP 常见函数的底层 C 代码实现原理，在自己的脑袋里对这个函数形成一个清晰的实现逻辑 ，这样这些函数相关的题目无论怎么变化都能够从容应对！

当然这也是为了回归最本质的安全研究方法 ：代码审计。也许通过阅读这些代码还能发现意外的收获！

针对每一个 PHP 函数的源码阅读，我会做这些事情：

- 给出这些 PHPH 函数的底层代码，重要的会附上注释
- 中文描述其完整逻辑流，黑色加粗
- 总结这次源码阅读没有深入的地方
- 给出测试这个函数特性的 PHP 代码

本文持续更新，目前阅读过的 PHP 函数包括：is_numeric、intval、strval

### PHP 底层源码阅读方法

讲解一下我的 PHP 源码阅读方法：

- 准备工具：Source Insight   下载地址：[https://www.cnblogs.com/dakewei/p/7993613.html](https://www.cnblogs.com/dakewei/p/7993613.html)
- PHP 源码（最新）：[http://php.net/downloads.php](http://php.net/downloads.php)
- 基础知识：C 语言以及 C 语言函数的特性、Ascii 码全部字符

PHP 库函数基本都在 php-src/ext 目录下面，一般的函数在 standard 目录，当然也有具体的函数库 socket。

查找一个库函数的源码（比如 intval），直接在 SourceInsight 里搜索项目：PHP_FUNCTION(intval)。

### is_numeric

```c
PHP_FUNCTION(is_numeric)
{
	zval *arg;                  // is_numeric 使用的时候传递的

	ZEND_PARSE_PARAMETERS_START(1, 1)
		Z_PARAM_ZVAL(arg)
	ZEND_PARSE_PARAMETERS_END();

	switch (Z_TYPE_P(arg)) {
		case IS_LONG:
		case IS_DOUBLE:
			RETURN_TRUE;
			break;

		case IS_STRING:
			if (is_numeric_string(Z_STRVAL_P(arg), Z_STRLEN_P(arg), NULL, NULL, 0)) {
				RETURN_TRUE;
			} else {
				RETURN_FALSE;
			}
			break;

		default:
			RETURN_FALSE;
			break;
	}
}
```

在这个函数里面主要是根据 is_numeric 传递的参数类型做出了不同的操作：



1. **如果是 long 或 double 类型直接返回逻辑 True**
2. **如果是字符串（CTF 常见的传入格式）会调用 is_numeric_string 判断这个字符串是否是数字** 
3. **其余情况返回 False**




下面我们跟踪 is_numeric_string 函数，调用了 is_numeric_string_ex

```c
static zend_always_inline zend_uchar is_numeric_string(const char *str, size_t length, zend_long *lval, double *dval, int allow_errors) {
    return is_numeric_string_ex(str, length, lval, dval, allow_errors, NULL);
}
```

继续跟踪 is_numeric_string_ex 函数：

```c
static zend_always_inline zend_uchar is_numeric_string_ex(const char *str, size_t length, zend_long *lval, double *dval, int allow_errors, int *oflow_info)
{
	if (*str > '9') {
		return 0;
	}
	return _is_numeric_string_ex(str, length, lval, dval, allow_errors, oflow_info);
}
```

可以看到 is_numeric_string_ex 函数逻辑如下：



1. **str 是你传递的字符串类型参数头指针，如果第一个字符就大于 '9' 的 ASCII，返回 False**
2. **否则调用 _is_numeric_string_ex 函数** 



继续跟踪 _is_numeric_string_ex 函数，因为其代码比较长，我只贴出核心的部分，其余部分用 ...... 代替：

```
# 其他使用的函数定义
#define ZEND_IS_DIGIT(c) ((c) >= '0' && (c) <= '9') // 用于判断一个字符 ASCII 是否在 '0'-'9' 之间

# _is_numeric_string_ex 函数定义
ZEND_API zend_uchar ZEND_FASTCALL _is_numeric_string_ex(const char *str, size_t length, zend_long *lval, double *dval, int allow_errors, int *oflow_info) 
{

    // 跳过开头这些空白字符
	while (*str == ' ' || *str == '\t' || *str == '\n' || *str == '\r' || *str == '\v' || *str == '\f') {
		str++;
		length--;
	}
	ptr = str;
 
    // 第一个字符如果是 + 或者 - 做个记录，对最后返回 True False 没有直接影响
	if (*ptr == '-') {
		neg = 1;
		ptr++;
	} else if (*ptr == '+') {
		ptr++;
	}

	if (ZEND_IS_DIGIT(*ptr)) {
		/* 跳过此时字符串开头的 0 数字字符 */
		while (*ptr == '0') {
			ptr++;
		}
         
         /*  for 循环开始依次判断字符的情况。如果有小数点或者指数符号 (e,E) 则是 double 类型。
          * 如果是 double 或者没有必要继续检查下去（遇到非数字字符），或者 long 类型的数字位数达到最大
          * 都停止 for 循环 */
		for (type = IS_LONG; !(digits >= MAX_LENGTH_OF_LONG && (dval || allow_errors == 1)); digits++, ptr++) {
check_digits:
			if (ZEND_IS_DIGIT(*ptr)) {
				......
			} else if (*ptr == '.' && dp_or_e < 1) {
				goto process_double;
			} else if ((*ptr == 'e' || *ptr == 'E') && dp_or_e < 2) {
				......
			}
			break;
		}

		if (digits >= MAX_LENGTH_OF_LONG) {
			......
			dp_or_e = -1;
			goto process_double;
		}
	} else if (*ptr == '.' && ZEND_IS_DIGIT(ptr[1])) {
        // double 数据类型处理
process_double:
		type = IS_DOUBLE;
         ......
	} else {
         // 这里会返回 False
		return 0;
	}

	if (ptr != str + length) {
         // 如果遇到非数字字符，for 循环提前结束，这个 if
         // 如果不允许报错则会返回 False
		if (!allow_errors) {
             // 这里会返回 False
			return 0;
		}
		if (allow_errors == -1) {
             // 如果允许报错则会抛出错误
			zend_error(E_NOTICE, "A non well formed numeric value encountered");
		}
	}
    
    // 返回 IS_DOUBLE 或者 IS_LONG，都是大于 0 的整数，最终 is_numeric 返回 True
	if (type == IS_LONG) {
		if (digits == MAX_LENGTH_OF_LONG - 1) {
                 ......
				return IS_DOUBLE;
			}
		}
         .......
		return IS_LONG;
	} else {
		.......
		return IS_DOUBLE;
	}
}
```

核心的程序骨架如上所示，总结起来逻辑流如下：



1. **跳过字符串开头的 空格、\t、\r、\n、\v、\f 这些字符（没有跳过 \0）**
2. **这时候第一个字符如果是 -或者+做个记录然后跳过** 
3. **调用 ZEND_IS_DIGIT 函数判断此时第一个字符 ASCII 是否在 '0' 到 '9' 之间，如果是继续执行第 4 步。如果不是，如果第一个字符是 "." 开头的，记录之后跳过重新判断新的字符串第一个字符是否满足 ASCII 是否在 '0' 到 '9' 之间，如果是执行第 5 步。否则返回 False**
4. **因为没有遇到小数点，先跳过全部的 '0' 字符执行第五步** 
5. **循环依次判断此时的字符串字符，可以处理 e 或 E 字符表示的指数形式，一直直到遇到字符的 ASCII 不在 '0' 到 '9' 之间停止循环，有效的数字字符串会被记录** 
6. **判断是否出现遇到非数字字符提前结束 for 循环的情况（包括数字字符串格式错误，比如二个小数点 or .234E23 也会导致 for 提前结束循环），返回 False （如果允许报错，会抛出代码里的那行错误）**
7. **返回 IS_LONG 或者 IS_DOUBLE 常量，无论是哪个，最终 is_numeric 都将返回 True**



可以看到这个函数只可能在第 3 步和第 6 步返回 False，至此分析完毕。-------------------------------------------------------End

我在本次分析中没有深入的点，可能存在研究价值：

- is_numeric 是用 Z_TYPE_P 判断变量类型，是否存在误判
- is_numeric 是用 Z_STRLEN_P 得到传递的参数的长度，其逻辑是否可靠
- _is_numeric_string_ex 具体哪些格式属于错误，需要被报错和返回 False

最后给出测试这个函数特性的 PHP 代码：

```php
<?php
$test = array(
    0=>"2333",
    1=>"\02333",2=>"\r2333",3=>"\n2333",4=>"\t\v2333",5=>"\f2333",
    6=>" 2333",
    7=>" \r\n+2333",8=>" \r\n\t\v-2333",
    8=>"Z2333",
    9=>" \f\n\v.2333",
    10=>" \f000000000000000.233330000000000000000",
    11=>" \v\r\n000.2303504320",
    12=>" \v0234E234",
    13=>2333,
    14=>2333.2333,
    15=>"999999999999999999999999999999999999999999999999999999999999999999999999999999999999",
    16=>2333333333333333333333.23333333333333333333333333333

);

foreach ($test as $key => $value){
    echo strval($key)." Test";
    var_dump(is_numeric($value));
    echo "<br>";
}

?>
```

### intval

### strval

### strcmp



### > 附录 之 ASCII 

常用的不可见字符和空白符：

| 符号 | ASCII 16 进制 |      含义      |
| ---- | :-----------: | :------------: |
| \0   |      00       | 空字符（NULL） |
| \r   |      0a       |     换行符     |
| \n   |      0d       | 归位键（回车） |
| \t   |      09       |   水平制表符   |
| \v   |      0b       |   垂直制表符   |
| \f   |      0c       |     换页符     |
| 空格 |      20       |                |

