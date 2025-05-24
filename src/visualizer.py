"""
可视化模块 - Person 3 负责开发
作者：Person 3 (可视化工程师)
功能：生成各种气象数据可视化图表
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class WeatherVisualizer:
    """气象数据可视化类"""
    
    def __init__(self):
        """初始化可视化器"""
        self.color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
    def plot_temperature_trend(self, data, save_path=None):
        """
        绘制温度趋势图
        
        Args:
            data: 包含日期和温度的DataFrame
            save_path: 保存路径
        """
        plt.figure(figsize=(12, 6))
        
        # 绘制温度趋势
        plt.plot(data['date'], data['temperature'], 
                color=self.color_palette[0], linewidth=2, alpha=0.8)
        
        # 添加移动平均线
        data['temp_ma7'] = data['temperature'].rolling(window=7).mean()
        plt.plot(data['date'], data['temp_ma7'], 
                color=self.color_palette[1], linewidth=2, 
                label='7天移动平均', alpha=0.7)
        
        plt.title('气温变化趋势图', fontsize=16, fontweight='bold')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('温度 (°C)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"温度趋势图已保存到: {save_path}")
        
        plt.show()
        
    def plot_seasonal_comparison(self, data, save_path=None):
        """
        绘制季节对比箱线图
        
        Args:
            data: 包含季节和气象数据的DataFrame
            save_path: 保存路径
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 温度对比
        sns.boxplot(data=data, x='season', y='temperature', 
                   palette=self.color_palette, ax=axes[0,0])
        axes[0,0].set_title('各季节温度分布', fontsize=14, fontweight='bold')
        axes[0,0].set_xlabel('季节')
        axes[0,0].set_ylabel('温度 (°C)')
        
        # 湿度对比
        sns.boxplot(data=data, x='season', y='humidity', 
                   palette=self.color_palette, ax=axes[0,1])
        axes[0,1].set_title('各季节湿度分布', fontsize=14, fontweight='bold')
        axes[0,1].set_xlabel('季节')
        axes[0,1].set_ylabel('湿度 (%)')
        
        # 降水对比
        sns.boxplot(data=data, x='season', y='precipitation', 
                   palette=self.color_palette, ax=axes[1,0])
        axes[1,0].set_title('各季节降水分布', fontsize=14, fontweight='bold')
        axes[1,0].set_xlabel('季节')
        axes[1,0].set_ylabel('降水量 (mm)')
        
        # 风速对比
        sns.boxplot(data=data, x='season', y='wind_speed', 
                   palette=self.color_palette, ax=axes[1,1])
        axes[1,1].set_title('各季节风速分布', fontsize=14, fontweight='bold')
        axes[1,1].set_xlabel('季节')
        axes[1,1].set_ylabel('风速 (km/h)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"季节对比图已保存到: {save_path}")
        
        plt.show()
        
    def plot_correlation_heatmap(self, data, save_path=None):
        """
        绘制相关性热力图
        
        Args:
            data: 气象数据DataFrame
            save_path: 保存路径
        """
        # 选择数值列
        numeric_cols = ['temperature', 'humidity', 'precipitation', 'wind_speed']
        correlation_matrix = data[numeric_cols].corr()
        
        plt.figure(figsize=(10, 8))
        
        # 绘制热力图
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   cmap='RdYlBu_r', 
                   center=0,
                   square=True,
                   fmt='.3f',
                   cbar_kws={'label': '相关系数'})
        
        plt.title('气象要素相关性分析', fontsize=16, fontweight='bold')
        plt.xlabel('气象要素')
        plt.ylabel('气象要素')
        
        # 设置标签
        labels = ['温度', '湿度', '降水量', '风速']
        plt.xticks(range(len(labels)), labels)
        plt.yticks(range(len(labels)), labels)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"相关性热力图已保存到: {save_path}")
        
        plt.show()
        
    def create_interactive_dashboard(self, data):
        """
        创建交互式仪表板
        
        Args:
            data: 气象数据DataFrame
            
        Returns:
            plotly图表对象
        """
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('温度趋势', '湿度分布', '降水量分析', '风速变化'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 温度趋势
        fig.add_trace(
            go.Scatter(x=data['date'], y=data['temperature'],
                      mode='lines', name='温度',
                      line=dict(color=self.color_palette[0], width=2)),
            row=1, col=1
        )
        
        # 湿度分布
        fig.add_trace(
            go.Histogram(x=data['humidity'], name='湿度分布',
                        marker_color=self.color_palette[1],
                        opacity=0.7),
            row=1, col=2
        )
        
        # 降水量分析
        fig.add_trace(
            go.Bar(x=data.groupby('season')['precipitation'].mean().index,
                  y=data.groupby('season')['precipitation'].mean().values,
                  name='平均降水量',
                  marker_color=self.color_palette[2]),
            row=2, col=1
        )
        
        # 风速变化
        fig.add_trace(
            go.Scatter(x=data['date'], y=data['wind_speed'],
                      mode='markers', name='风速',
                      marker=dict(color=self.color_palette[3], size=4)),
            row=2, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title_text="气象数据交互式仪表板",
            title_x=0.5,
            height=600,
            showlegend=False
        )
        
        # 更新坐标轴标签
        fig.update_xaxes(title_text="日期", row=1, col=1)
        fig.update_yaxes(title_text="温度 (°C)", row=1, col=1)
        
        fig.update_xaxes(title_text="湿度 (%)", row=1, col=2)
        fig.update_yaxes(title_text="频次", row=1, col=2)
        
        fig.update_xaxes(title_text="季节", row=2, col=1)
        fig.update_yaxes(title_text="降水量 (mm)", row=2, col=1)
        
        fig.update_xaxes(title_text="日期", row=2, col=2)
        fig.update_yaxes(title_text="风速 (km/h)", row=2, col=2)
        
        return fig
        
    def plot_weather_patterns(self, data, save_path=None):
        """
        绘制天气模式分析图
        
        Args:
            data: 气象数据DataFrame
            save_path: 保存路径
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 温度-湿度散点图
        scatter = axes[0,0].scatter(data['temperature'], data['humidity'], 
                                  c=data['precipitation'], 
                                  cmap='Blues', alpha=0.6, s=30)
        axes[0,0].set_xlabel('温度 (°C)')
        axes[0,0].set_ylabel('湿度 (%)')
        axes[0,0].set_title('温度-湿度关系（颜色表示降水量）')
        plt.colorbar(scatter, ax=axes[0,0], label='降水量 (mm)')
        
        # 月度平均温度
        monthly_temp = data.groupby(data['date'].dt.month)['temperature'].mean()
        axes[0,1].plot(monthly_temp.index, monthly_temp.values, 
                      marker='o', linewidth=2, markersize=6,
                      color=self.color_palette[1])
        axes[0,1].set_xlabel('月份')
        axes[0,1].set_ylabel('平均温度 (°C)')
        axes[0,1].set_title('月度平均温度变化')
        axes[0,1].grid(True, alpha=0.3)
        
        # 降水量分布
        axes[1,0].hist(data['precipitation'], bins=30, 
                      color=self.color_palette[2], alpha=0.7, edgecolor='black')
        axes[1,0].set_xlabel('降水量 (mm)')
        axes[1,0].set_ylabel('频次')
        axes[1,0].set_title('降水量分布直方图')
        
        # 风速玫瑰图（简化版）
        wind_bins = pd.cut(data['wind_speed'], bins=5, labels=['微风', '轻风', '和风', '清风', '强风'])
        wind_counts = wind_bins.value_counts()
        axes[1,1].pie(wind_counts.values, labels=wind_counts.index, 
                     autopct='%1.1f%%', colors=self.color_palette)
        axes[1,1].set_title('风速等级分布')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"天气模式分析图已保存到: {save_path}")
        
        plt.show()
        
    def generate_all_visualizations(self, data, output_dir='results'):
        """
        生成所有可视化图表
        
        Args:
            data: 气象数据DataFrame
            output_dir: 输出目录
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("🎨 Person 3 正在生成可视化图表...")
        
        # 生成各种图表
        self.plot_temperature_trend(data, f'{output_dir}/temperature_trend.png')
        self.plot_seasonal_comparison(data, f'{output_dir}/seasonal_comparison.png')
        self.plot_correlation_heatmap(data, f'{output_dir}/correlation_heatmap.png')
        self.plot_weather_patterns(data, f'{output_dir}/weather_patterns.png')
        
        # 生成交互式仪表板
        interactive_fig = self.create_interactive_dashboard(data)
        interactive_fig.write_html(f'{output_dir}/interactive_dashboard.html')
        print(f"交互式仪表板已保存到: {output_dir}/interactive_dashboard.html")
        
        print("✅ Person 3 的可视化模块完成！")
        
        return {
            'temperature_trend': f'{output_dir}/temperature_trend.png',
            'seasonal_comparison': f'{output_dir}/seasonal_comparison.png',
            'correlation_heatmap': f'{output_dir}/correlation_heatmap.png',
            'weather_patterns': f'{output_dir}/weather_patterns.png',
            'interactive_dashboard': f'{output_dir}/interactive_dashboard.html'
        }

if __name__ == "__main__":
    # 测试代码
    print("Person 3 可视化模块测试")
    
    # 创建示例数据进行测试
    import pandas as pd
    from datetime import datetime, timedelta
    
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(100)]
    test_data = pd.DataFrame({
        'date': dates,
        'temperature': np.random.normal(15, 10, 100),
        'humidity': np.random.normal(60, 15, 100),
        'precipitation': np.random.exponential(2, 100),
        'wind_speed': np.random.gamma(2, 3, 100),
        'season': ['春季'] * 25 + ['夏季'] * 25 + ['秋季'] * 25 + ['冬季'] * 25
    })
    
    # 测试可视化器
    visualizer = WeatherVisualizer()
    visualizer.plot_temperature_trend(test_data) 