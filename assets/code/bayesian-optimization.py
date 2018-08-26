# encoding:utf-8
# 参考文献：贝叶斯优化调参 笔记前面这些链接，代码来自http://36kr.com/p/5114423.html
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


# mpl.rc('font', family='Times New Roman')
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'SimSun,Times New Roman'

def polyfit(x, y, degree):
    results = {}
    coeffs = np.polyfit(x, y, degree)
    f = np.poly1d(coeffs)
    results['function'] = f
    results['polynomial'] = coeffs.tolist()
    # r-squared
    p = np.poly1d(coeffs)
    # fit values, and mean
    yhat = p(x)  # or [p(z) for z in x]
    ybar = np.sum(y) / len(y)  # or sum(y)/len(y)
    ssreg = np.sum((yhat - ybar) ** 2)  # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar) ** 2)  # or sum([ (yi - ybar)**2 for yi in y])
    results['determination'] = ssreg / sstot  # 准确率
    return results

x = [0,1,5,10,17,20,24,26,30,34,36,38,40]
y = [-95,-40,8,20,43,48,54,47,22,22,24,22,21]
z1 = polyfit(x, y, 8)
all_x = np.linspace(0,40,100)
f = z1['function']

x_obs = [0, 10, 20, 30] # 初始值  训练数据  会变化
y_obs = []  # 初始值  训练数据  会变化
for x in x_obs:
    y = f(x)
    y_obs.append(y)

beta = 2
def k(xs,xs2,sigma=1,l=1):

    # Pairwise difference matrix
    dx = np.expand_dims(xs,1)-np.expand_dims(xs2,0)
    return (sigma ** 2) * np.exp(-((dx / l) ** 2) / 2)


def m(x):
    """The mean function. As discussed, we can let the mean always be zero"""
    return np.zeros_like(x)

def acq(mu_s, sigma_s, beta=beta):
    # 根据最大收获函数返回下一个采样最可能的位置
    eva = mu_s + sigma_s * beta
    return np.where(eva == np.max(eva))[0][0]

stop_w = []
def stop():
    stop_num = 10
    if len(stop_w) < stop_num:
        pass
    else:
        recent_w = stop_w[-stop_num:]
        if len(set(recent_w))==1:
            return True
    if len(x_obs) == len(X):
        return True
    return False

x = 0 # 储存当前采样点
y = 0 # 储存当前采样点经过f的结果
W = 0 # 储存次数最大的f执行结果
X = np.linspace(0, 40, 41) # 变量全部取值空间
other_x = [] # 存放所有不在x_obs的x

xs = [] # 采样点 只起记录的作用和x_obs额外增加的元素同步
fs = [] # 样本点
init_x_obs = x_obs
init_y_obs = y_obs
# x_obs = [-4,-2,0] # 初始值  训练数据  会变化
# y_obs = [4.48, 4.44, 6.0]  # 初始值  训练数据  会变化

# 选取第一个计算出来的均值和方差在于此时other_x最大
first_state = 1
first_other_x = []
first_mu_s = None
first_sigma_s = None

# test_K = k(x_obs,2)
# print test_K
while not stop():
    other_x = [item for item in X if item not in x_obs]
    K = k(x_obs, x_obs)
    K_s = k(x_obs, other_x)
    K_ss = k(other_x, other_x)
    K_sTKinv = np.matmul(K_s.T, np.linalg.pinv(K))
    # print np.matmul(K_sTKinv, y_obs-m(x_obs)).size
    mu_s = m(other_x) + np.matmul(K_sTKinv, y_obs-m(x_obs))
    Sigma_s = K_ss - np.matmul(K_sTKinv, K_s)
    sigma_s = np.diag(Sigma_s)
    if first_state<=8:
        first_state += 1
        first_mu_s = mu_s
        first_sigma_s = sigma_s
        first_other_x = other_x
    next_pos = acq(mu_s, sigma_s)

    x = other_x[next_pos]
    y = f(x)
    xs.append(x)
    fs.append(y)
    x_obs.append(x)
    y_obs.append(y)
    W = max(y_obs)
    stop_w.append(W)

all_x = np.linspace(0, 40, 100)
mu_f = polyfit(first_other_x, first_mu_s, 8)['function']
sigma_f = polyfit(first_other_x, first_sigma_s, 8)['function']
show = 8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
plt.figure()
plt.plot(all_x, mu_f(all_x), "b-", label="均值")  # 20 - 32
plt.xlim(0, 40)
plt.ylim(-10, 60)
plt.plot(all_x, mu_f(all_x) + show * sigma_f(all_x), "w-")
plt.plot(all_x, mu_f(all_x) - show * sigma_f(all_x), "w-")
plt.fill_between(all_x, mu_f(all_x) + show * sigma_f(all_x), mu_f(all_x) - show * sigma_f(all_x), facecolor="lightgray",
                 label="不确定性")
plt.plot(init_x_obs, init_y_obs, linestyle="none", marker="o", label="初始样本点")
plt.plot(xs, fs, linestyle="none", marker="*", label="采样点")
plt.plot(all_x, f(all_x), "--", label="拟合的函数关系")
plt.legend(loc="upper left", fontsize=10.5)
plt.xlabel("max-pattern-len", fontname="Times New Roman", fontsize=10.5)
plt.ylabel("W", fontname="Times New Roman", fontsize=10.5)
plt.xticks(fontsize=10.5, fontname="Times New Roman")
plt.yticks(fontsize=10.5, fontname="Times New Roman")
plt.show()