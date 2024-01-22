
#题目
# 假设你正在爬楼梯。需要 n 阶你才能到达楼顶。
# 每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？
#分析
#第n个台阶只能从第n-1或者n-2个上来。到第n-1个台阶的走法 + 第n-2个台阶的走法 = 到第n个台阶的走法


def climbStairs(n):

    #创建一个列表，包含需要第一和第二台阶所需要的步数
    StepList=[1,2]
    Step=0
    
    #算法精髓：

    #从第三台阶开始，按照上面的算法：n=(n-2)+(n-1)，一层一层算出每个台阶所需要的步数。每次算完都放进列表StepList
    if n>=3:
        for j in range(3,n+1):
            print("j=",j)
            StepList.append(StepList[j-3]+StepList[j-2])#利用上一个和上上一个台阶所需步数，算出爬上本台阶所需要的步数。
        #算完后取出列表最后一个数，也就是爬上最后一个台阶所需要的步数    
        Step=StepList[j-1]
    else:#爬上第二和第一台阶所需要的步数，因这两个台阶没有上一个和上上一个台阶，故特殊处理
        Step=StepList[n-1]    
    print("StepList=",StepList)
    print("Step=",Step)
    return Step

climbStairs(2)