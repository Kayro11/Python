# -*- coding: utf-8 -*-
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import datetime
import os


def process_csv_to_html(file_path, output_dir, y_range=None, 
                             time_threshold=0.5, use_markers=False, log_callback=None, progress_callback=None):
    """
    绘制PCI随时间变化的RSRP趋势图（无平滑处理）：
    当一个PCI在同一时间点有多个SSB Idx时，取SSS-RSRP最大的值作为该PCI的当前值
    新增参数use_markers: 是否显示标记点（大量数据时建议关闭以提升性能）
    新增参数log_callback: 日志回调函数，用于输出处理进度
    新增参数progress_callback: 进度回调函数，用于返回处理百分比(0-100)
    """
    # 初始化进度回调（0%）
    if progress_callback:
        progress_callback(0.0)
    
    # ===== 读取CSV文件（添加读取阶段log）=====
    if log_callback:
        log_callback(f"开始处理文件：{file_path}")
        log_callback(f"尝试读取CSV文件（支持分号/逗号分隔）...")
    
    # 读取CSV文件（支持分号/逗号分隔）
    try:
        if log_callback:
            log_callback(f"尝试编码：utf-8，分隔符：;")
        df = pd.read_csv(file_path, encoding='utf-8', sep=';')
        if len(df.columns) <= 1:
            if log_callback:
                log_callback(f"分号分隔失败，尝试编码：utf-8，分隔符：,")
            df = pd.read_csv(file_path, encoding='utf-8', sep=',')
    except UnicodeDecodeError:
        try:
            if log_callback:
                log_callback(f"utf-8编码失败，尝试编码：gbk，分隔符：;")
            df = pd.read_csv(file_path, encoding='gbk', sep=';')
            if len(df.columns) <= 1:
                if log_callback:
                    log_callback(f"分号分隔失败，尝试编码：gbk，分隔符：,")
                df = pd.read_csv(file_path, encoding='gbk', sep=',')
        except Exception as e:
            if log_callback:
                log_callback(f"文件读取失败：{str(e)}")
            raise ValueError(f"文件编码或格式错误：{str(e)}")
    except Exception as e:
        if log_callback:
            log_callback(f"文件读取失败：{str(e)}")
        raise ValueError(f"读取CSV失败：{str(e)}")
    
    if log_callback:
        log_callback(f"CSV文件读取成功，原始数据共 {len(df)} 行，{len(df.columns)} 列")
    
    # 进度更新：10%
    if progress_callback:
        progress_callback(10.0)
    
    # ===== 检查必要列（添加列检查log）=====
    if log_callback:
        log_callback(f"开始检查必要列...")
    required_cols = ['Date', 'Time', 'PCI', 'SSB Idx', 'SSS-RSRP']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        if log_callback:
            log_callback(f"检查失败：缺少必要列 {missing_cols}")
        raise ValueError(
            f"CSV文件缺少必要列：{missing_cols}\n"
            f"已尝试分号和逗号分隔，请检查列名或分隔符。"
        )
    if log_callback:
        log_callback(f"检查通过：所有必要列（{required_cols}）均存在")
    
    # 进度更新：20%
    if progress_callback:
        progress_callback(20.0)
    
    # ===== 合并日期时间（添加时间处理log）=====
    if log_callback:
        log_callback(f"开始合并日期时间列（精确到毫秒）...")
    
    # 合并日期时间为DateTime列（精确到毫秒）
    def combine_datetime(row):
        if pd.isna(row['Date']) or pd.isna(row['Time']):
            return None
        # 处理日期：日.月.年 -> 年-月-日
        date_parts = str(row['Date']).split('.')
        if len(date_parts) != 3:
            return None  # 格式错误
        day, month, year = date_parts
        if len(year) == 2:
            year = f"20{year}"  # 假设为20xx年
        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"  # 补零确保两位
        
        # 处理时间：时:分:秒.毫秒 -> 保留3位毫秒
        time_str = str(row['Time'])
        if '.' not in time_str:
            time_str += '.000'  # 补全毫秒
        else:
            ms_part = time_str.split('.')[1]
            if len(ms_part) < 3:
                time_str = time_str.ljust(len(time_str) + (3 - len(ms_part)), '0')
            else:
                time_str = time_str[:time_str.index('.') + 4]  # 只保留3位毫秒
        return pd.to_datetime(f"{date_str} {time_str}", format='%Y-%m-%d %H:%M:%S.%f')
    
    df['DateTime'] = df.apply(combine_datetime, axis=1)
    invalid_datetime = df['DateTime'].isna().sum()
    if log_callback:
        log_callback(f"日期时间转换完成：共 {invalid_datetime} 行无效日期时间格式，{len(df) - invalid_datetime} 行有效")
    
    # 进度更新：30%
    if progress_callback:
        progress_callback(30.0)
    
    # ===== 转换数值列并过滤（添加数值处理log）=====
    if log_callback:
        log_callback(f"开始转换数值列（PCI、SSB Idx、SSS-RSRP）...")
    
    # 转换数值列并过滤无效数据
    df['PCI'] = pd.to_numeric(df['PCI'], errors='coerce').astype('Int64')
    df['SSB Idx'] = pd.to_numeric(df['SSB Idx'], errors='coerce')
    df['SSS-RSRP'] = pd.to_numeric(df['SSS-RSRP'], errors='coerce')
    
    # 统计数值转换无效的行数
    invalid_pci = df['PCI'].isna().sum()
    invalid_ssb = df['SSB Idx'].isna().sum()
    invalid_rsrp = df['SSS-RSRP'].isna().sum()
    if log_callback:
        log_callback(f"数值转换完成：无效PCI {invalid_pci} 行，无效SSB Idx {invalid_ssb} 行，无效SSS-RSRP {invalid_rsrp} 行")
        log_callback(f"开始过滤无效数据（保留DateTime、PCI、SSB Idx、SSS-RSRP均有效的行）...")
    
    filtered_df = df.dropna(subset=['DateTime', 'PCI', 'SSB Idx', 'SSS-RSRP']).sort_values('DateTime')
    if filtered_df.empty:
        if log_callback:
            log_callback(f"过滤后无有效数据，处理终止")
        raise ValueError("过滤后无有效数据，请检查数据格式（如日期时间格式、数值格式）")
    
    if log_callback:
        log_callback(f"数据过滤完成：有效数据共 {len(filtered_df)} 行")
    
    # 进度更新：40%
    if progress_callback:
        progress_callback(40.0)
    
    # ===== 核心计算：取每个PCI时间点的最大RSRP（添加计算log）=====
    if log_callback:
        log_callback(f"开始核心计算：每个PCI在每个时间点保留SSS-RSRP最大的记录...")
    
    # 核心逻辑：每个PCI在每个时间点，只保留SSS-RSRP最大的SSB Idx记录
    pci_max_rsrp = filtered_df.sort_values(
        by=['PCI', 'DateTime', 'SSS-RSRP'], 
        ascending=[True, True, False]  # 按PCI升序、时间升序、RSRP降序
    ).groupby(['PCI', 'DateTime']).head(1).reset_index(drop=True)
    
    # 计算总处理行数（去重后的有效数据行数）
    total_rows = len(pci_max_rsrp)
    if total_rows == 0:
        if log_callback:
            log_callback(f"去重后无有效数据，处理终止")
        raise ValueError("处理后无有效数据，无法生成图表")
    
    if log_callback:
        log_callback(f"核心计算完成：去重后有效数据共 {total_rows} 行，涉及PCI数量：{len(pci_max_rsrp['PCI'].unique())} 个")
    
    # 直接使用原始SSS-RSRP值（无平滑处理）
    pci_max_rsrp['SSS-RSRP Original'] = pci_max_rsrp['SSS-RSRP']

    # 进度更新：50%
    if progress_callback:
        progress_callback(50.0)
    
    # ===== 创建图表（保留原有进度log）=====
    if log_callback:
        log_callback(f"开始生成图表...")
    
    fig = go.Figure()
    color_sequence = px.colors.qualitative.Plotly
    pci_list = sorted(pci_max_rsrp['PCI'].unique())
    mode = 'lines+markers' if use_markers else 'lines'
    processed_rows = 0
    
    for i, pci in enumerate(pci_list):
        group_df = pci_max_rsrp[pci_max_rsrp['PCI'] == pci].copy()
        if group_df.empty:
            continue
        group_df = group_df.sort_values('DateTime')
        
        # 按时间阈值分割曲线
        time_diff = group_df['DateTime'].diff().dt.total_seconds()
        group_df.loc[time_diff > time_threshold, 'SSS-RSRP Original'] = float('nan')
        
        # 分配颜色并添加曲线
        color_idx = i % len(color_sequence)
        trace_color = color_sequence[color_idx]
        hover_bgcolor = f"rgba{tuple(int(trace_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}"
        
        fig.add_trace(go.Scatter(
            x=group_df['DateTime'],
            y=group_df['SSS-RSRP Original'],
            mode=mode,
            name=f'PCI={pci}',
            line=dict(width=2, color=trace_color),
            marker=dict(size=4, color=trace_color) if use_markers else None,
            hovertemplate=(
                f'<br>时间: %{{x|%Y-%m-%d %H:%M:%S.%f}}<br>'
                f'RSRP (原始): %{{y:.1f}} dBm<br>'
                f'PCI: {pci}<br>'
                f'最强SSB Idx: %{{customdata}}<extra></extra>'
            ),
            customdata=group_df['SSB Idx'],
            hoverlabel=dict(
                bgcolor=hover_bgcolor,
                font=dict(color='black'),
                bordercolor=trace_color
            )
        ))
        
        # 更新进度log和进度回调
        processed_rows += len(group_df)
        progress = 50 + (processed_rows / total_rows) * 40  # 50%-90%区间
        if log_callback:
            log_callback(
                f"处理进度：{progress:.2f}% "
                f"（已处理 {processed_rows}/{total_rows} 行，当前PCI：{pci}）"
            )
        if progress_callback:
            progress_callback(progress)
    
    # ===== 配置布局并保存（添加输出log）=====
    file_base = os.path.splitext(os.path.basename(file_path))[0]
    now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if y_range is None:
        all_original = pci_max_rsrp['SSS-RSRP Original'].dropna()
        if not all_original.empty:
            min_val = all_original.min()
            max_val = all_original.max()
            y_range = [min_val * 1.1, max_val * 0.9]
            if log_callback:
                log_callback(f"自动计算Y轴范围：{y_range}")
        else:
            if log_callback:
                log_callback(f"无有效RSRP数据，使用默认Y轴范围")
    
    fig.update_layout(
        title=f'{file_base} (PCI的RSRP趋势，取最强SSB Idx原始值)',
        xaxis_title='时间',
        yaxis_title='SSS-RSRP（原始值，dBm）',
        yaxis=dict(range=y_range, fixedrange=True) if y_range else dict(fixedrange=True),
        legend=dict(title='PCI列表', orientation='v', yanchor='top'),
        template='plotly_white',
        hovermode='x unified',
        dragmode='pan',
        margin=dict(l=60, r=30, t=60, b=40)
    )
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{file_base}_pci_rsrp_original_{now_str}.html')
    
    if log_callback:
        log_callback(f"开始生成HTML文件：{output_path}（使用Canvas渲染器优化性能）")
    
    fig.write_html(
        output_path,
        include_plotlyjs='inline',
        config={
            'scrollZoom': True,
            'toImageButtonOptions': {'format': 'png', 'filename': f'{file_base}_pci_rsrp_original', 'scale': 2},
            'renderer': 'canvas',
            'displayModeBar': True,
            'showTips': False
        }
    )
    
    # 进度更新：100%
    if progress_callback:
        progress_callback(100.0)
    
    if log_callback:
        log_callback(f"HTML文件生成完成：{output_path}")
    
    return output_path


if __name__ == "__main__":
    input_csv = "test_sss_rsrp.csv"  # 替换为你的CSV文件路径
    output_directory = "html_output"   # 输出目录
    try:
        # 示例日志回调函数（命令行输出）
        def log_callback(msg):
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")
        
        # 示例进度回调函数
        def progress_callback(percent):
            print(f"处理进度：{percent:.2f}%")
        
        html_path = process_csv_to_html(
            input_csv, 
            output_directory,
            time_threshold=0.5,
            use_markers=False,
            log_callback=log_callback,
            progress_callback=progress_callback
        )
        print(f"PCI的原始RSRP趋势图表已生成：{html_path}")
    except Exception as e:
        print(f"处理失败：{str(e)}")