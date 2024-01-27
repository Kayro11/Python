import tkinter as tk


#定义后续使用的变量的值
MainWindow=[]#显示窗口的名称
MainLabel=['Piperf']#主横幅显示的文字

#创建绘画窗口
window=tk.Tk()
window.title(MainWindow)#传入窗口名称


#找到屏幕中心点，减去窗口长宽的一半，窗口对齐到屏幕中心
def get_ScreenSize():
    "计算屏幕大小对应的窗口大小和位置，返回窗口（宽度，高度 ，x坐标，y坐标）"
    ScreenWidth=window.winfo_screenwidth()
    ScreenHeight=window.winfo_screenheight()
    WindowWidth=0
    WindowHeight=0
    print('ScreenWidth=%d' %ScreenWidth)
    print('ScreenHeight=%d' %ScreenHeight)
    if ScreenHeight<=1080:
        WindowWidth=500
        WindowHeight=300
        sw=(ScreenWidth/2)-(WindowWidth/2)
        sh=(ScreenHeight/2)-(WindowHeight/2)


    else :
        WindowWidth=1000
        WindowHeight=600
        sw=(ScreenWidth/2)-(WindowWidth/2)
        sh=(ScreenHeight/2)-(WindowHeight/2)

    return WindowWidth,WindowHeight,sw,sh

window.geometry("%dx%d+%d+%d" %(get_ScreenSize()))#传入窗口位置（宽度x高度 +x坐 +y坐标）

#创建标签
MainLabel=tk.Label(window,text=MainLabel,bg='grey',font='Arial,12',width=100,height=1)
MainLabel.pack()

#创建输入窗口
entry1=tk.Entry(window,show=None,font=('Arial',14),width=20)
entry1.place(x=20,y=50)
entry2=tk.Entry(window,show=None,font=('Arial',14),width=8)
entry2.place(x=200,y=50)

#按键变量：开始/停止
click = False
click_text=tk.StringVar()
click_text.set('开始')

#按键状态切换函数，click的值False表示灌包停止，True表示灌包开始
def Click_Button():
    global click
    global click_text
    if click  ==False :
        click = True
        click_text.set('停止')#click的值变True，按钮显示停止
    
    else:
        click = False
        click_text.set('开始')#click的值变True，按钮显示停止


Button=tk.Button(window,textvariable=click_text,font={'Arial',12},width=10,height=1,command=Click_Button)
Button.place(x=230,y=48)


#循环
window.mainloop()