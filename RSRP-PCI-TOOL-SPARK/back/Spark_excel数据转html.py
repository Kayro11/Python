# -*- coding: utf-8 -*-
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import datetime
import os


def process_file_to_html(file_path, output_dir, y_range=[-110, -75], 
                         rolling_window=4, time_threshold=0.5):
    """
    处理Excel或CSV文件并转换为HTML图表
    
    参数:
        file_path: 文件路径（支持.xlsx和.csv格式）
        output_dir: HTML输出目录
        y_range: Y轴范围
        rolling_window: 平滑窗口大小
        time_threshold: 时间间隔阈值(秒)
    
    返回:
        生成的HTML文件路径
    """
    # 根据文件扩展名判断类型并读取
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.xlsx':
        # Excel文件：使用原逻辑，sheet名与文件名相同
        sheet_name = os.path.splitext(os.path.basename(file_path))[0]
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    elif file_ext == '.csv':
        # CSV文件：直接读取（假设编码为utf-8，可根据需要调整）
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        raise ValueError(f"不支持的文件格式：{file_ext}，仅支持.xlsx和.csv")
    
    # 时间格式转换
    def convert_time(s):
        if pd.isna(s) or len(str(s)) < 17:
            return None
        s = str(s)
        ms = s[16:]
        ms = ms.ljust(6, '0')
        return f"{s[:4]}-{s[4:6]}-{s[6:8]} {s[9:11]}:{s[11:13]}:{s[13:15]}.{ms}"
    
    # 在df['PCI']转换前添加
    print("PCI列原始数据类型：", df['PCI'].dtype)
    print("PCI列前5行数据：\n", df['PCI'].head())
    print("PCI列中非数字内容：\n", df[~df['PCI'].astype(str).str.match(r'^-?\d+(\.\d+)?$')]['PCI'].unique())

    df['TIMESTAMP'] = df['TIMESTAMP'].ffill().astype(str)
    df['Time'] = df['TIMESTAMP'].apply(convert_time)
    df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
    #df['PCI'] = pd.to_numeric(df['PCI'], errors='coerce').fillna(-1).astype(int)  # 用-1代替NaN（根据业务调整）
    df['PCI'] = pd.to_numeric(df['PCI'], errors='coerce').astype('Int64')
    filtered_df = df.dropna(subset=['PCI'])
    
    # 创建图表
    fig = go.Figure()
    for pci, pci_df in filtered_df.groupby('PCI'):
        if not pci_df.empty:
            pci_df = pci_df.copy()
            pci_df['SSB RSRP Smooth'] = pci_df['SSB RSRP'].rolling(
                window=rolling_window, center=True
            ).mean()
            time_diff = pci_df['Time'].diff().dt.total_seconds()
            pci_df.loc[time_diff > time_threshold, 'SSB RSRP Smooth'] = float('nan')
            fig.add_trace(go.Scatter(
                x=pci_df['Time'],
                y=pci_df['SSB RSRP Smooth'],
                mode='lines',
                name=f'PCI={pci}'
            ))
    
    # 布局配置
    file_base = os.path.splitext(os.path.basename(file_path))[0]
    now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    fig.update_layout(
        title=file_base,
        xaxis_title='时间',
        yaxis_title='SSB RSRP',
        yaxis=dict(range=y_range, fixedrange=True),
        legend=dict(title='PCI', orientation='v'),
        template='plotly_white',
        hovermode='x unified',
        dragmode='pan'
    )
    
    # 保存HTML
    output_path = os.path.join(output_dir, f'{file_base}_{now_str}.html')
    fig.write_html(
        output_path,
        include_plotlyjs='inline',
        config={'scrollZoom': True}
    )
    
    return output_path