"""
气象数据分析Web应用 - Person 3 负责开发
作者：Person 3 (可视化工程师)
功能：基于Streamlit的交互式气象数据分析平台
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from data_processor import WeatherDataProcessor
    from visualizer import WeatherVisualizer
    from ai_analyzer import WeatherAIAnalyzer
except ImportError as e:
    st.error(f"模块导入错误: {e}")
    st.info("请确保所有必要的模块都已正确安装和配置")

# 页面配置
st.set_page_config(
    page_title="智能气象数据分析平台",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class WeatherApp:
    """气象数据分析Web应用类"""
    
    def __init__(self):
        """初始化应用"""
        self.processor = None
        self.visualizer = None
        self.ai_analyzer = None
        self.data = None
        self.filtered_data = None
        
        # 初始化组件
        try:
            self.processor = WeatherDataProcessor()
            self.visualizer = WeatherVisualizer()
            self.ai_analyzer = WeatherAIAnalyzer()
        except Exception as e:
            st.error(f"组件初始化失败: {e}")
    
    def load_data(self):
        """加载或生成数据，并支持上传自定义数据"""
        # 优先检查用户是否上传了自己的CSV数据
        uploaded_file = st.sidebar.file_uploader("上传你的CSV数据文件", type="csv")
        if uploaded_file is not None:
            try:
                # 尝试读取上传的CSV数据
                data = pd.read_csv(uploaded_file)
                # 请确保CSV中包含 'date' 列，并转换为datetime格式
                if 'date' not in data.columns:
                    st.error("上传的数据中未找到 'date' 列，请检查数据格式。")
                else:
                    data['date'] = pd.to_datetime(data['date'], errors='coerce')
                    self.data = data
                    st.success("自定义数据加载成功！")
            except Exception as e:
                st.error(f"自定义数据加载失败: {e}")
                st.info("将加载默认示例数据。")
        
        # 如果没有上传数据或上传失败，则使用示例数据
        if self.data is None:
            with st.spinner("正在生成示例气象数据..."):
                try:
                    # 检查处理器是否存在
                    if self.processor is None:
                        st.error("数据处理器未初始化")
                        return None
                    
                    # 生成示例数据，并进行数据清洗预处理
                    raw_data = self.processor.generate_sample_data()
                    self.data = self.processor.clean_data(raw_data)
                    st.success("示例数据加载成功！")
                except Exception as e:
                    st.error(f"数据加载失败: {e}")
                    return None
        return self.data
    
    def show_sidebar(self):
        """显示侧边栏"""
        st.sidebar.markdown("## 🌤️ 导航菜单")
        
        # 页面选择
        page = st.sidebar.selectbox(
            "选择页面",
            ["📊 数据概览", "📈 可视化分析", "🤖 AI智能分析", "ℹ️ 项目介绍"]
        )
        
        st.sidebar.markdown("---")
        
        # 数据控制
        st.sidebar.markdown("### 📋 数据控制")
        
        if st.sidebar.button("🔄 重新生成示例数据"):
            self.data = None
            # 兼容处理：检查是否存在 experimental_rerun，如果不存在则提示用户手动刷新
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            else:
                st.info("请手动刷新页面以重新生成示例数据。")
        
        # 数据筛选
        if self.data is not None:
            st.sidebar.markdown("### 🔍 数据筛选")
            
            # 日期范围选择
            date_range = st.sidebar.date_input(
                "选择日期范围",
                value=(self.data['date'].min().date(), self.data['date'].max().date()),
                min_value=self.data['date'].min().date(),
                max_value=self.data['date'].max().date()
            )
            
            # 季节选择
            seasons = st.sidebar.multiselect(
                "选择季节",
                options=self.data['season'].unique(),
                default=self.data['season'].unique()
            )
            
            # 应用筛选
            if len(date_range) == 2 and seasons:
                mask = (
                    (self.data['date'].dt.date >= date_range[0]) &
                    (self.data['date'].dt.date <= date_range[1]) &
                    (self.data['season'].isin(seasons))
                )
                self.filtered_data = self.data[mask]
            else:
                self.filtered_data = self.data
        
        return page
    
    def show_data_overview(self):
        """显示数据概览页面"""
        st.markdown('<h1 class="main-header">📊 气象数据概览</h1>', unsafe_allow_html=True)
        
        data = self.load_data()
        if data is None:
            return
        
        # 使用筛选后的数据
        display_data = self.filtered_data if self.filtered_data is not None else data
        
        # 基本统计信息
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📅 数据天数",
                value=len(display_data),
                delta=f"共{len(data)}天数据"
            )
        
        with col2:
            avg_temp = display_data['temperature'].mean()
            st.metric(
                label="🌡️ 平均温度",
                value=f"{avg_temp:.1f}°C",
                delta=f"{avg_temp - data['temperature'].mean():.1f}°C"
            )
        
        with col3:
            avg_humidity = display_data['humidity'].mean()
            st.metric(
                label="💧 平均湿度",
                value=f"{avg_humidity:.1f}%",
                delta=f"{avg_humidity - data['humidity'].mean():.1f}%"
            )
        
        with col4:
            total_precip = display_data['precipitation'].sum()
            st.metric(
                label="🌧️ 总降水量",
                value=f"{total_precip:.1f}mm",
                delta=f"{total_precip - data['precipitation'].sum():.1f}mm"
            )
        
        st.markdown("---")
        
        # 数据表格
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<h2 class="sub-header">📋 数据详情</h2>', unsafe_allow_html=True)
            st.dataframe(
                display_data.head(20),
                use_container_width=True,
                hide_index=True
            )
            
            # 下载按钮
            csv = display_data.to_csv(index=False)
            st.download_button(
                label="📥 下载数据 (CSV)",
                data=csv,
                file_name=f"weather_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.markdown('<h2 class="sub-header">📈 统计摘要</h2>', unsafe_allow_html=True)
            stats = display_data[['temperature', 'humidity', 'precipitation', 'wind_speed']].describe()
            st.dataframe(stats, use_container_width=True)
            st.markdown("### 🍂 季节分布")
            season_counts = display_data['season'].value_counts()
            fig_pie = px.pie(
                values=season_counts.values,
                names=season_counts.index,
                title="数据季节分布"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    def show_visualization_analysis(self):
        """显示可视化分析页面"""
        st.markdown('<h1 class="main-header">📈 可视化分析</h1>', unsafe_allow_html=True)
        
        data = self.load_data()
        if data is None:
            return
        
        display_data = self.filtered_data if self.filtered_data is not None else data
        
        chart_type = st.selectbox(
            "选择图表类型",
            ["温度趋势图", "季节对比分析", "相关性分析", "天气模式分析", "交互式仪表板"]
        )
        
        if chart_type == "温度趋势图":
            self.show_temperature_trend(display_data)
        elif chart_type == "季节对比分析":
            self.show_seasonal_comparison(display_data)
        elif chart_type == "相关性分析":
            self.show_correlation_analysis(display_data)
        elif chart_type == "天气模式分析":
            self.show_weather_patterns(display_data)
        elif chart_type == "交互式仪表板":
            self.show_interactive_dashboard(display_data)
    
    def show_temperature_trend(self, data):
        """显示温度趋势图"""
        st.markdown('<h2 class="sub-header">🌡️ 温度趋势分析</h2>', unsafe_allow_html=True)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['temperature'],
            mode='lines',
            name='日温度',
            line=dict(color='#1f77b4', width=1),
            opacity=0.7
        ))
        
        data_copy = data.copy()
        data_copy['temp_ma7'] = data_copy['temperature'].rolling(window=7).mean()
        data_copy['temp_ma30'] = data_copy['temperature'].rolling(window=30).mean()
        
        fig.add_trace(go.Scatter(
            x=data_copy['date'],
            y=data_copy['temp_ma7'],
            mode='lines',
            name='7天移动平均',
            line=dict(color='#ff7f0e', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=data_copy['date'],
            y=data_copy['temp_ma30'],
            mode='lines',
            name='30天移动平均',
            line=dict(color='#2ca02c', width=3)
        ))
        
        fig.update_layout(
            title="温度变化趋势",
            xaxis_title="日期",
            yaxis_title="温度 (°C)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("最高温度", f"{data['temperature'].max():.1f}°C")
        with col2:
            st.metric("最低温度", f"{data['temperature'].min():.1f}°C")
        with col3:
            st.metric("温度范围", f"{data['temperature'].max() - data['temperature'].min():.1f}°C")
    
    def show_seasonal_comparison(self, data):
        """显示季节对比分析"""
        st.markdown('<h2 class="sub-header">🍂 季节对比分析</h2>', unsafe_allow_html=True)
        
        variable = st.selectbox(
            "选择分析变量",
            ["temperature", "humidity", "precipitation", "wind_speed"],
            format_func=lambda x: {"temperature": "温度", "humidity": "湿度", 
                                   "precipitation": "降水量", "wind_speed": "风速"}[x]
        )
        
        variable_names = {"temperature": "温度", "humidity": "湿度", 
                          "precipitation": "降水量", "wind_speed": "风速"}
        
        fig = px.box(
            data, 
            x='season', 
            y=variable,
            title=f"各季节{variable_names[variable]}分布",
            color='season'
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        seasonal_stats = data.groupby('season')[variable].agg(['mean', 'std', 'min', 'max']).round(2)
        seasonal_stats.columns = ['平均值', '标准差', '最小值', '最大值']
        st.dataframe(seasonal_stats, use_container_width=True)
    
    def show_correlation_analysis(self, data):
        """显示相关性分析"""
        st.markdown('<h2 class="sub-header">🔗 相关性分析</h2>', unsafe_allow_html=True)
        
        numeric_cols = ['temperature', 'humidity', 'precipitation', 'wind_speed']
        corr_matrix = data[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="气象要素相关性热力图",
            color_continuous_scale="RdBu_r"
        )
        
        labels = ['温度', '湿度', '降水量', '风速']
        fig.update_xaxes(ticktext=labels, tickvals=list(range(len(labels))))
        fig.update_yaxes(ticktext=labels, tickvals=list(range(len(labels))))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📝 相关性解释")
        st.markdown("""
        - **正相关 (红色)**：两个变量同时增加或减少
        - **负相关 (蓝色)**：一个变量增加时另一个减少
        - **无相关 (白色)**：两个变量之间没有线性关系
        """)
    
    def show_weather_patterns(self, data):
        """显示天气模式分析"""
        st.markdown('<h2 class="sub-header">🌦️ 天气模式分析</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.scatter(
                data,
                x='temperature',
                y='humidity',
                color='precipitation',
                size='wind_speed',
                title="温度-湿度关系图",
                labels={'temperature': '温度 (°C)', 'humidity': '湿度 (%)', 
                        'precipitation': '降水量 (mm)', 'wind_speed': '风速 (km/h)'}
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            monthly_temp = data.groupby(data['date'].dt.month)['temperature'].mean()
            fig2 = px.line(
                x=monthly_temp.index,
                y=monthly_temp.values,
                title="月度平均温度变化",
                labels={'x': '月份', 'y': '平均温度 (°C)'}
            )
            fig2.update_traces(mode='lines+markers')
            st.plotly_chart(fig2, use_container_width=True)
        
        fig3 = px.histogram(
            data,
            x='precipitation',
            nbins=30,
            title="降水量分布直方图",
            labels={'precipitation': '降水量 (mm)', 'count': '频次'}
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    def show_interactive_dashboard(self, data):
        """显示交互式仪表板"""
        st.markdown('<h2 class="sub-header">📊 交互式仪表板</h2>', unsafe_allow_html=True)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('温度趋势', '湿度分布', '降水量分析', '风速变化'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        fig.add_trace(
            go.Scatter(x=data['date'], y=data['temperature'],
                       mode='lines', name='温度',
                       line=dict(color='#1f77b4', width=2)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Histogram(x=data['humidity'], name='湿度分布',
                         marker_color='#ff7f0e', opacity=0.7),
            row=1, col=2
        )
        
        seasonal_precip = data.groupby('season')['precipitation'].mean()
        fig.add_trace(
            go.Bar(x=seasonal_precip.index, y=seasonal_precip.values,
                   name='平均降水量', marker_color='#2ca02c'),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=data['date'], y=data['wind_speed'],
                       mode='markers', name='风速',
                       marker=dict(color='#d62728', size=4)),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    def show_ai_analysis(self):
        """显示AI分析页面"""
        st.markdown('<h1 class="main-header">🤖 AI智能分析</h1>', unsafe_allow_html=True)
        
        data = self.load_data()
        if data is None:
            return
        
        display_data = self.filtered_data if self.filtered_data is not None else data
        
        st.markdown('<div class="info-box">💡 本页面展示AI驱动的智能气象数据分析结果</div>', unsafe_allow_html=True)
        
        analysis_type = st.selectbox(
            "选择AI分析类型",
            ["异常检测", "智能报告生成", "预测分析"]
        )
        
        if analysis_type == "异常检测":
            self.show_anomaly_detection(display_data)
        elif analysis_type == "智能报告生成":
            self.show_ai_report(display_data)
        elif analysis_type == "预测分析":
            self.show_prediction_analysis(display_data)
    
    def show_anomaly_detection(self, data):
        """显示异常检测结果"""
        st.markdown('<h2 class="sub-header">🔍 异常天气检测</h2>', unsafe_allow_html=True)
        
        if self.ai_analyzer is None:
            st.error("AI分析器未初始化，无法进行异常检测")
            st.info("正在使用模拟数据进行演示...")
            anomaly_indices = np.random.choice(data.index, size=min(10, len(data)//10), replace=False)
            simulated_anomalies = data.loc[anomaly_indices]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("异常天气天数", len(simulated_anomalies))
            with col2:
                st.metric("异常率", f"{len(simulated_anomalies)/len(data)*100:.2f}%")
            with col3:
                st.metric("正常天气天数", len(data) - len(simulated_anomalies))
            
            st.dataframe(simulated_anomalies, use_container_width=True)
            return
        
        with st.spinner("AI正在分析异常天气..."):
            try:
                anomalies_result = self.ai_analyzer.detect_anomalies(data)
                if isinstance(anomalies_result, tuple):
                    anomalies, anomaly_info = anomalies_result
                else:
                    anomalies = anomalies_result
                    anomaly_info = None
                
                anomaly_count = len(anomalies) if hasattr(anomalies, '__len__') else 0
                anomaly_rate = (anomaly_count / len(data)) * 100 if len(data) > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("异常天气天数", anomaly_count)
                with col2:
                    st.metric("异常率", f"{anomaly_rate:.2f}%")
                with col3:
                    st.metric("正常天气天数", len(data) - anomaly_count)
                
                fig = go.Figure()
                if hasattr(anomalies, 'index') and len(anomalies) > 0:
                    normal_data = data[~data.index.isin(anomalies.index)]
                    
                    fig.add_trace(go.Scatter(
                        x=normal_data['date'].values,
                        y=normal_data['temperature'].values,
                        mode='markers',
                        name='正常天气',
                        marker=dict(color='blue', size=4)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=anomalies['date'].values,
                        y=anomalies['temperature'].values,
                        mode='markers',
                        name='异常天气',
                        marker=dict(color='red', size=8, symbol='x')
                    ))
                else:
                    fig.add_trace(go.Scatter(
                        x=data['date'].values,
                        y=data['temperature'].values,
                        mode='markers',
                        name='正常天气',
                        marker=dict(color='blue', size=4)
                    ))
                
                fig.update_layout(
                    title="异常天气检测结果",
                    xaxis_title="日期",
                    yaxis_title="温度 (°C)",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                if hasattr(anomalies, 'empty') and not anomalies.empty:
                    st.markdown("### 🚨 异常天气详情")
                    st.dataframe(anomalies, use_container_width=True)
                elif anomaly_count == 0:
                    st.info("🎉 未检测到异常天气！")
                
            except Exception as e:
                st.error(f"异常检测失败: {e}")
                st.info("正在使用模拟数据进行演示...")
                anomaly_indices = np.random.choice(data.index, size=min(10, len(data)//10), replace=False)
                simulated_anomalies = data.loc[anomaly_indices]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("异常天气天数", len(simulated_anomalies))
                with col2:
                    st.metric("异常率", f"{len(simulated_anomalies)/len(data)*100:.2f}%")
                with col3:
                    st.metric("正常天气天数", len(data) - len(simulated_anomalies))
                
                st.dataframe(simulated_anomalies, use_container_width=True)
    
    def show_ai_report(self, data):
        """显示AI生成的报告"""
        st.markdown('<h2 class="sub-header">📝 AI智能报告</h2>', unsafe_allow_html=True)
        
        if self.ai_analyzer is None:
            st.error("AI分析器未初始化，无法生成报告")
            st.info("请检查OpenAI API配置和模块依赖")
            return
        
        if st.button("🤖 生成AI分析报告"):
            with st.spinner("AI正在生成分析报告..."):
                try:
                    report = self.ai_analyzer.generate_insights_report(data)
                    st.markdown("### 📊 AI分析报告")
                    st.markdown(report)
                except Exception as e:
                    st.error(f"报告生成失败: {e}")
                    st.info("请检查OpenAI API配置")
    
    def show_prediction_analysis(self, data):
        """显示预测分析"""
        st.markdown('<h2 class="sub-header">🔮 预测分析</h2>', unsafe_allow_html=True)
        
        st.info("🚧 预测功能正在开发中，敬请期待！")
        
        st.markdown("### 📈 趋势分析")
        data_copy = data.copy()
        data_copy['day_of_year'] = data_copy['date'].dt.dayofyear
        
        from sklearn.linear_model import LinearRegression
        
        X = data_copy[['day_of_year']]
        y = data_copy['temperature']
        
        model = LinearRegression()
        model.fit(X, y)
        
        trend_slope = model.coef_[0]
        
        if trend_slope > 0:
            trend_text = f"📈 温度呈上升趋势，每天平均上升 {trend_slope:.4f}°C"
        else:
            trend_text = f"📉 温度呈下降趋势，每天平均下降 {abs(trend_slope):.4f}°C"
        
        st.markdown(f"**{trend_text}**")
    
    def show_project_info(self):
        """显示项目介绍页面"""
        st.markdown('<h1 class="main-header">ℹ️ 项目介绍</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        ## 🌤️ 智能气象数据分析平台
        
        ### 📋 项目概述
        本项目是一个基于Python的智能气象数据分析平台，集成了数据处理、可视化、AI分析等功能。
        
        ### 👥 团队分工
        - **Person 1 (组长)**: 项目架构、环境配置、代码整合
        - **Person 2**: 数据处理模块开发
        - **Person 3**: 可视化和Web应用开发 ⭐
        - **Person 4**: AI分析功能开发
        - **Person 5**: 文档和报告编写
        
        ### 🛠️ 技术栈
        - **编程语言**: Python
        - **数据处理**: Pandas, NumPy
        - **可视化**: Matplotlib, Seaborn, Plotly
        - **Web框架**: Streamlit
        - **机器学习**: Scikit-learn
        - **AI集成**: OpenAI GPT
        - **环境管理**: Conda
        
        ### 🎯 主要功能
        1. **数据处理**: 气象数据生成、清洗、预处理
        2. **可视化分析**: 多种图表类型，交互式仪表板
        3. **AI智能分析**: 异常检测、智能报告生成
        4. **Web应用**: 基于Streamlit的用户友好界面
        
        ### 📊 Person 3 的贡献
        作为可视化工程师，Person 3 负责开发了：
        - `src/visualizer.py`: 完整的可视化模块
        - `app/streamlit_app.py`: 本Web应用
        - 多种图表类型和交互功能
        - 用户友好的界面设计
        
        ### 🚀 如何使用
        1. 在侧边栏选择不同的功能页面
        2. 使用数据筛选功能自定义分析范围
        3. 探索各种可视化图表
        4. 体验AI智能分析功能
        
        ### 📞 联系信息
        如有问题或建议，请联系开发团队。
        """)
        
        st.markdown("### 📈 技术统计")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("代码行数", "500+")
        with col2:
            st.metric("功能模块", "4个")
        with col3:
            st.metric("图表类型", "10+种")
        with col4:
            st.metric("页面数量", "4个")
    
    def run(self):
        """运行应用"""
        page = self.show_sidebar()
        if page == "📊 数据概览":
            self.show_data_overview()
        elif page == "📈 可视化分析":
            self.show_visualization_analysis()
        elif page == "🤖 AI智能分析":
            self.show_ai_analysis()
        elif page == "ℹ️ 项目介绍":
            self.show_project_info()

def main():
    """主函数"""
    app = WeatherApp()
    app.run()

if __name__ == "__main__":
    main()
