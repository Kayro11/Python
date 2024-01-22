import tkinter as tk
#定义后续使用的变量的值
MainWindow=[]
MainLabel=['Piperf']
WindowWidth=500
WindowHeight=300
#创建绘画窗口
window=tk.Tk()
window.title(MainWindow)
ScreenWidth=window.winfo_screenwidth()
ScreenHeight=window.winfo_screenheight()
ScreenWidth=(ScreenWidth/2)-(WindowWidth/2)
ScreenHeight=(ScreenHeight/2)-(WindowHeight/2)
window.geometry("%dx%d+%d+%d" %(WindowWidth,WindowHeight,ScreenWidth,ScreenHeight))#找到屏幕中心点，减去窗口长宽的一半，窗口对齐到屏幕中心

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