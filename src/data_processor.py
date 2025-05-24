"""
数据处理模块
负责人：Person 2 (2001wzh)
功能：数据获取、清洗、预处理
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

class WeatherDataProcessor:
    def __init__(self):
        self.data_dir = "data"
        self.raw_dir = os.path.join(self.data_dir, "raw")
        self.processed_dir = os.path.join(self.data_dir, "processed")
        self._create_directories()
    
    def _create_directories(self):
        """创建数据目录"""
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
    
    def generate_sample_data(self, start_date='2023-01-01', end_date='2023-12-31'):
        """生成示例气象数据"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(42)
        
        # 生成温度数据（带季节性）
        day_of_year = dates.dayofyear
        temp_base = 15 + 10 * np.sin(2 * np.pi * day_of_year / 365.25)
        temperature = temp_base + np.random.normal(0, 3, len(dates))
        
        # 生成湿度数据
        humidity = 65 + 15 * np.random.randn(len(dates))
        humidity = np.clip(humidity, 0, 100)
        
        # 生成降水数据
        precipitation = np.random.exponential(scale=3, size=len(dates))
        precipitation = np.where(np.random.random(len(dates)) < 0.7, 0, precipitation)
        
        # 生成风速数据
        wind_speed = np.random.gamma(2, 2, len(dates))
        
        data = pd.DataFrame({
            'date': dates,
            'temperature': np.round(temperature, 1),
            'humidity': np.round(humidity, 1),
            'precipitation': np.round(precipitation, 1),
            'wind_speed': np.round(wind_speed, 1)
        })
        
        # 保存原始数据
        data.to_csv(os.path.join(self.raw_dir, 'weather_data.csv'), index=False)
        return data
    
    def clean_data(self, df):
        """数据清洗"""
        df_clean = df.copy()
        
        # 温度异常值处理
        df_clean['temperature'] = df_clean['temperature'].clip(-50, 50)
        
        # 湿度范围限制
        df_clean['humidity'] = df_clean['humidity'].clip(0, 100)
        
        # 降水量不能为负
        df_clean['precipitation'] = df_clean['precipitation'].clip(0, None)
        
        # 添加衍生特征
        df_clean['month'] = pd.to_datetime(df_clean['date']).dt.month
        df_clean['season'] = pd.cut(
            df_clean['month'], 
            bins=[0, 3, 6, 9, 12], 
            labels=['冬季', '春季', '夏季', '秋季'],
            include_lowest=True
        )
        
        # 保存清洗后的数据
        df_clean.to_csv(os.path.join(self.processed_dir, 'weather_data_clean.csv'), index=False)
        return df_clean
    
    def get_statistics(self, df):
        """获取数据统计信息"""
        stats = {
            'basic_stats': df.describe(),
            'missing_values': df.isnull().sum(),
            'data_types': df.dtypes,
            'correlation': df.select_dtypes(include=[np.number]).corr()
        }
        return stats

if __name__ == "__main__":
    processor = WeatherDataProcessor()
    data = processor.generate_sample_data()
    clean_data = processor.clean_data(data)
    stats = processor.get_statistics(clean_data)
    print("数据处理模块开发完成！")
    print(f"数据形状: {clean_data.shape}")