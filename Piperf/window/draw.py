import tkinter as tk


#定义后续使用的变量的值
MainWindow=[]#显示窗口的名称
MainLabel=['Piperf']#主横幅显示的文字

window=tk.Tk()#创建绘画窗口
window.title(MainWindow)#传入窗口名称


switch_text=tk.StringVar()#iperf版本切换控制


click = False#按键变量：开始/停止  click的值False表示灌包停止，True表示灌包开始
click_text=tk.StringVar()
click_text.set('开始')

#创建标签
MainLabel=tk.Label(window, textvariable=switch_text,bg='#09c',font='Arial,12',height=1)
MainLabel.pack(fill='x')

#创建框架，放置下面的组件
frame=tk.Frame(window)#放入frame2和frame3
frame.pack(fill='both',side='top', expand=0)

frame1=tk.LabelFrame(window, relief='sunken')#放入输出text
frame1.pack(fill='both',side='top', expand=1)

frame2=tk.Frame(frame)#iperf版本切换按钮
frame2.grid(column=1,row=0,sticky=tk.W)

frame3=tk.Frame(frame)#输入窗口和开始按钮
frame3.grid(column=1,row=1)


#switch_button2.invoke()  #调用按钮

#标签1
label1=tk.Label(frame,text='iPerf版本：',font=('Arial',18),height=1)
label1.grid(column=0,row=0,sticky=tk.W)

#标签2
label2=tk.Label(frame,text='IP地址和端口号：',font=('Arial',18),height=1)
label2.grid(column=0,row=1)

#标签3
label3=tk.Label(frame,text='Powered by Kayro11\nkayro-11@outlook.com',font=('Arial',8),justify='left')
label3.grid(column=1,row=0,sticky=tk.E)

#找到屏幕中心点，减去窗口长宽的一半，窗口对齐到屏幕中心
def get_ScreenSize():
    "计算屏幕大小对应的窗口大小和位置，返回窗口（宽度，高度 ，x坐标，y坐标）"
    ScreenWidth=window.winfo_screenwidth()
    ScreenHeight=window.winfo_screenheight()
    WindowWidth=0
    WindowHeight=0
    #print('ScreenWidth=%d' %ScreenWidth)
    #print('ScreenHeight=%d' %ScreenHeight)


    if ScreenHeight<=1080:
        WindowWidth=610
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


#创建切换iperf的按钮
switch_button1=tk.Radiobutton(frame2,text='iPerf2',font='Arial,12',variable=switch_text,value='iPerf2')
switch_button1.select()
switch_button2=tk.Radiobutton(frame2,text='iPerf3',font='Arial,12',variable=switch_text,value='iPerf3')
switch_button1.pack(fill='y', side='left')
switch_button2.pack(fill='y', side='left')




#创建输入窗口
entry1=tk.Entry(frame3,show=None,font=('Arial',14),width=20)
entry2=tk.Entry(frame3,show=None,font=('Arial',14),width=8)
entry1.grid(column=0,row=0)
entry2.grid(column=1,row=0)

#创建滑动条，和输出窗口绑定
scrollbar=tk.Scrollbar(frame1)
scrollbar.pack(side='right',fill='y')

#创建输出text
text=tk.Text(frame1,yscrollcommand=scrollbar.set)
text.pack(fill='both',expand=1)

#滑动条绑定输出窗口
scrollbar.config(command=text.yview)


#按键状态切换函数，click的值False表示灌包停止，True表示灌包开始
def Click_Button():
    global click
    global click_text
    global text

    if click  ==False :
        click = True
        click_text.set('停止')#click的值变True，按钮显示停止

        #停止后解锁按钮
        entry1.config(state='readonly')
        entry2.config(state='readonly')
        switch_button1.config(state='disabled')
        switch_button2.config(state='disabled')

        text.insert('end','================================='+'开始'+'('+entry1.get()+':'+entry2.get()+')'+'================================='+'\n')


    else:
        click = False
        click_text.set('开始')#click的值变True，按钮显示停止

        #停止后解锁按钮
        entry1.config(state='normal')
        entry2.config(state='normal')
        switch_button1.config(state='normal')
        switch_button2.config(state='normal')

        text.insert('end','================================='+'停止'+'('+entry1.get()+':'+entry2.get()+')'+'================================='+'\n')


Button1=tk.Button(frame3,textvariable=click_text,font={'Arial',12},width=10,height=1,command=Click_Button)
Button1.grid(column=2,row=0)



#循环
window.mainloop()