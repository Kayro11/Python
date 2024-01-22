import tkinter as tk
#定义后续使用的变量的值
MainWindow=[]
MainLabel=['Piperf']
#创建绘画窗口
window=tk.Tk()
window.title(MainWindow)


def get_ScreenSize():
    "计算屏幕大小对应的窗口大小和位置"
    ScreenWidth=window.winfo_screenwidth()
    ScreenHeight=window.winfo_screenheight()
    WindowWidth=0
    WindowHeight=0
    print('ScreenWidth=%d' %ScreenWidth)
    print('ScreenHeight=%d' %ScreenHeight)
    if ScreenHeight<=1080:
        WindowWidth=500
        WindowHeight=300
        sw=(ScreenWidth/3)-(WindowWidth/3)
        sh=(ScreenHeight/3)-(WindowHeight/3)
        print(sw)
        print(sh)

    else :
        WindowWidth=1000
        WindowHeight=600
        sw=(ScreenWidth/2)-(WindowWidth/2)
        sh=(ScreenHeight/2)-(WindowHeight/2)
        print(sw)
        print(sh)
    return WindowWidth,WindowHeight,sw,sh

window.geometry("%dx%d+%d+%d" %(get_ScreenSize()))

#找到屏幕中心点，减去窗口长宽的一半，窗口对齐到屏幕中心

#创建标签
MainLabel=tk.Label(window,text=MainLabel,bg='grey',font='Arial,12',width=100,height=1)
MainLabel.pack()
#创建输入窗口
entry1=tk.Entry(window,show=None,font=('Arial',14),width=20)
entry1.place(x=20,y=50)
entry2=tk.Entry(window,show=None,font=('Arial',14),width=8)
entry2.place(x=200,y=50)
#循环
window.mainloop()