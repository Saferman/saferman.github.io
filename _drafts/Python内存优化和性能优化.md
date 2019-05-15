

### 跟踪内存分配——tracemalloc

工欲善其事必先利其器

The tracemalloc module is a debug tool to trace memory blocks allocated by Python. It provides the following information:

- Traceback where an object was allocated
- Statistics on allocated memory blocks per filename and per line number: total size, number and average size of allocated memory blocks
- Compute the differences between two snapshots to detect memory leaks

### 内存优化——类的属性

每个类都有一个 `__dict__`属性，包含了这类的属性，同样，如果我们创建了实例，每个实例也有一个 `__dict__` 属性，它里面就是当前的实例属性。实例的 `__dict__` 和类的 `__dict__` 是有所区别的，即实例属性和类属性是不同的。

我们可以根据一个类创建无数的实例，新建一个实例以后，又创建了一个新的 `__dict__`非常消耗内存，可以采用`__slots__`。一个类有了`__slots__`属性后后就不会有`__dict__`属性了，`__slots__`

这个属性能够优化内存的原因是，对于给类的`__slots__`的属性赋过值得属性，新建的实例拥有相同的属性值，但是不能修改（可读）。但是对于尚未赋值的`__slots__`属性在实例中仍然可以赋值，但是实例的属性修改不会影响类的属性的值。

测试代码：

```python
class Sample:
    name = 'rocky'
print(Sample.__dict__) # 
s = Sample()  
print(s.__dict__) # {}
s.age = 23
print(s.__dict__) # {'age': 23}
print(s.name)# rocky  因为实例没有这个属性就去类的属性寻找
Sample.name = "Alice"  
print(s.name) # Alice，还是会去寻找修改过的类的属性
s.name="rocky"
print(s.__dict__) # {'age': 23, 'name': 'rocky'} 有自己的name属性
print(Sample.name) # Alice
Sample.name = "Alice" 
print(s.name) # rocky 有自己的name属性，读取实例的类属性
```

```python
class Nature:
    __slots__ = ('tree','flower')

print(dir(Nature)) # 只有__slots__没有__dict__
print(Nature.__slots__) # ('tree', 'flower')
Nature.tree = 'liushu'
x = Nature()
print(x.__slots__) # ('tree', 'flower')
y = Nature()
print(y.__slots__) # ('tree', 'flower')
print(id(x.__slots__),id(y.__slots__)) # 2000135876296 2000135876296
print(x.tree,y.tree) # liushu liushu
# x.tree = 'taoshu' 不可修改
# 对实例属性来说，类的静态数据是只读的，不能修改，只有通过类属性才能修改。
x.flower = 'rose'
print(x.flower,Nature.flower) # rose <member 'flower' of 'Nature' objects>
Nature.flower = "hua"
print(x.flower,Nature.flower) # hua hua
```

总结，`__slots__`可以用于需要新建多个实例的类、同时实例共享类的属性值的场景。

### 内存泄漏和循环引用

内存泄露是让所有程序员都闻风丧胆的问题，轻则导致程序运行速度减慢，重则导致程序崩溃；

而循环引用是使用了引用计数的数据结构、编程语言都需要解决的问题。

推荐一篇文章：[使用gc、objgraph干掉python内存泄露与循环引用！](https://www.cnblogs.com/xybaby/p/7491656.html)

可以通过id()查看一个对象的“地址”，如果通过变量修改对象的值，但id没发生变化，那么就是mutable（列表），否则就是immutable（int类型）。

判断两个变量是否相等（值相同）使用==， 而判断两个变量是否指向同一个对象使用 is。比如下面a1 a2这两个变量指向的都是空的列表，值相同，但是不是同一个对象。

```python
>>> a1, a2 = [], []
>>> a1 == a2
True
>>> a1 is a2
False
```

> 当一个对象理论上（或者逻辑上）不再被使用了，但事实上没有被释放，那么就存在内存泄露；当一个对象事实上已经不可达（unreachable），即不能通过任何变量找到这个对象，但这个对象没有立即被释放，那么则可能存在循环引用。

引用计数（References count），指的是每个Python对象都有一个计数器，记录着当前有多少个变量指向这个对象。当计数器归零的时候，代表这个对象再也没有地方可能使用了，因此可以将对象安全的销毁。

通过sys.getrefcount(obj)对象可以获得一个对象的引用数目，返回值是真实引用数目加1（加1的原因是obj被当做参数传入了getrefcount函数）：

```
import sys
s = "sbcd"
print(sys.getrefcount(s)) # 4
a=1
print(sys.getrefcount(a)) # 1805  对象缓冲池会缓存十分常用的immutable对象；注意2.7版本是123
a=1000
print(sys.getrefcount(a)) # 4 
```

循环引用，就是一个对象直接或者间接引用自己本身，引用链形成一个环。

**python中狭义的垃圾回收，是指当出现循环引用，引用计数无计可施的时候采取的垃圾清理算法。**

既然Python中通过引用计数和垃圾回收来管理内存，那么什么情况下还会产生内存泄露呢？有两种情况：

1. **第一是对象被另一个生命周期特别长的对象所引用**，比如网络服务器，可能存在一个全局的单例ConnectionManager，管理所有的连接Connection，如果当Connection理论上不再被使用的时候，没有从ConnectionManager中删除，那么就造成了内存泄露。
2. **第二是循环引用中的对象定义了__del__函数**，这个在《[程序员必知的Python陷阱与缺陷列表](http://www.cnblogs.com/xybaby/p/7183854.html)》一文中有详细介绍，简而言之，如果定义了__del__函数，那么在循环引用中Python解释器无法判断析构对象的顺序，因此就不做处理。

如何查找内存泄漏：

> 如果我们怀疑一段代码、一个模块可能会导致内存泄露，那么首先调用一次obj.show_growth()，然后调用相应的函数，最后再次调用obj.show_growth()，看看是否有增加的对象。

```python
# -*- coding: utf-8 -*-
import objgraph

_cache = []

class OBJ(object):
    pass

def func_to_leak():
    o  = OBJ()
    _cache.append(o)
    # do something with o, then remove it from _cache 

    if True: # this seem ugly, but it always exists
        return 
    _cache.remove(o)

if __name__ == '__main__':
    objgraph.show_growth()
    try:
        func_to_leak()
    except:
        pass
    print 'after call func_to_leak'
    objgraph.show_growth()
```

gc module 处理内存泄漏。

### 参考链接

[tracemalloc 官方手册](https://docs.python.org/3/library/tracemalloc.html)

[__slots__代替__dict__优化内存](https://zhuanlan.zhihu.com/p/43114510)

[使用gc、objgraph干掉python内存泄露与循环引用！](https://www.cnblogs.com/xybaby/p/7491656.html)

《Python源码剖析》

[](https://jackywu.github.io/articles/python%E5%86%85%E5%AD%98%E6%B3%84%E9%9C%B2%E8%B0%83%E8%AF%95%E6%8C%87%E5%AF%BC%E6%80%9D%E6%83%B3/)

[记一次 Python 内存泄漏的排查](http://cosven.me/blogs/54)