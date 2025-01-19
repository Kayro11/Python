# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt

# 从 CSV 文件中读取数据
#df = pd.read_csv('C:\Users\毕拉力\OneDrive - bjtu.edu.cn\文档\Source\Python\RSRP-PCI-TOOL\2025.07.30_060230_DT_第四_华为mate40-1_NR Serving Cell RSRP(All Beam)[dBm].csv')
df = pd.read_csv(
        './2025.07.30_060230_DT_第四_华为mate40-1_NR PCI.csv',
    #'./NR5G_2025.07.22_110936_DT_第六趟_pctel-Scan-1.csv',
    encoding='utf-8'
)
# 设置图片清晰度
#plt.rcParams['figure.dpi'] = 120

# 设置图片比例为16:9
plt.figure(figsize=(16, 9))

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False    # 正确显示负号

# 转换为日期时间类型
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S.%f')
#df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S.%f')


# 转换为日期时间类型（毫秒补零到微秒）
df['Time'] = pd.to_datetime(df['Time'].str.pad(12, side='right', fillchar='0'), format='%H:%M:%S.%f')

# 只保留 需要的PCI数据
df = df[(df['NR PCI'] <= 40)&(df['NR PCI'] > 30)]
# 按照 NR PCI 列进行分组，并遍历每个分组
for pci, group in df.groupby('NR PCI'):
    plt.plot(group['Time'], group['NR Serving Cell RSRP(All Beam)[dBm]'], label=f'PCI {pci}')

# 设置图表标题和坐标轴标签
plt.title('7月30号第四趟测试-华为手机车内RSRP覆盖情况')
plt.xlabel('时间')
plt.ylabel('NR Serving Cell RSRP(All Beam)[dBm]')

# 显示图例
#plt.legend()
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

# 自动调整布局
#plt.tight_layout()

# 显示图表
plt.show()