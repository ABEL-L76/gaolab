"""
AI分析模块
负责人：Person 4 (lumos-0)
功能：提供基于AI的气象数据分析，如异常检测、洞察报告生成等。
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest # 用于异常检测
# import openai # 如果要对接OpenAI API，取消此行注释
import os

class WeatherAIAnalyzer:
    def __init__(self, openai_api_key=None):
        """
        初始化AI分析器。
        :param openai_api_key: (可选) OpenAI API密钥。
        """
        self.openai_api_key = openai_api_key
        # if self.openai_api_key:
        #     try:
        #         openai.api_key = self.openai_api_key
        #         print("OpenAI API key configured.")
        #     except Exception as e:
        #         print(f"Error configuring OpenAI: {e}")
        # else:
        #     print("OpenAI API key not provided. AI report generation will use template.")
        pass

    def detect_anomalies(self, df, features=['temperature', 'humidity', 'precipitation', 'wind_speed'], contamination='auto', random_state=42):
        """
        使用Isolation Forest检测数据中的异常点。
        :param df: 输入的DataFrame，包含日期和指定的特征列。
        :param features: 用于检测异常的特征列表。
        :param contamination: 数据集中异常点的比例，'auto'由算法决定。
        :param random_state: 随机种子，保证结果可复现。
        :return: 一个包含异常数据的DataFrame，以及一个包含异常信息的元组 (anomalies_df, info_dict)。
                 如果无异常或出错，anomalies_df可能为空。
        """
        if df.empty or not all(feature in df.columns for feature in features):
            print("Error: DataFrame is empty or missing required features for anomaly detection.")
            return pd.DataFrame(), {"message": "Data is empty or features are missing."}

        df_analysis = df[features].copy()
        df_analysis.fillna(df_analysis.mean(), inplace=True) # 简单处理缺失值

        if df_analysis.empty or len(df_analysis) < 2: # Isolation Forest 需要至少2个样本
             print("Warning: Not enough data points for anomaly detection after preprocessing.")
             return pd.DataFrame(), {"message": "Not enough data for anomaly detection."}

        try:
            model = IsolationForest(contamination=contamination, random_state=random_state)
            model.fit(df_analysis)
            
            # 预测异常 (-1 表示异常, 1 表示正常)
            df['anomaly_score'] = model.decision_function(df_analysis)
            df['is_anomaly'] = model.predict(df_analysis)
            
            anomalies_df = df[df['is_anomaly'] == -1].copy()
            
            anomaly_info = {
                "total_points_analyzed": len(df),
                "anomalies_found": len(anomalies_df),
                "features_used": features,
                "contamination_setting": contamination
            }
            
            if not anomalies_df.empty:
                print(f"Detected {len(anomalies_df)} anomalies.")
            else:
                print("No anomalies detected with the current settings.")
            
            return anomalies_df, anomaly_info
            
        except Exception as e:
            print(f"Error during anomaly detection: {e}")
            return pd.DataFrame(), {"message": f"Error during anomaly detection: {e}"}

    def get_data_summary(self, df):
        """
        生成数据的文本摘要。
        :param df: 输入的DataFrame。
        :return: 文本摘要字符串。
        """
        if df.empty:
            return "数据为空，无法生成摘要。"
        
        summary_parts = []
        if 'temperature' in df.columns:
            avg_temp = df['temperature'].mean()
            max_temp = df['temperature'].max()
            min_temp = df['temperature'].min()
            summary_parts.append(f"平均温度为 {avg_temp:.1f}°C (最高 {max_temp:.1f}°C, 最低 {min_temp:.1f}°C)。")
        
        if 'humidity' in df.columns:
            avg_humidity = df['humidity'].mean()
            summary_parts.append(f"平均湿度为 {avg_humidity:.1f}%。")

        if 'precipitation' in df.columns:
            total_precipitation = df['precipitation'].sum()
            rainy_days = df[df['precipitation'] > 0].shape[0]
            summary_parts.append(f"总降水量为 {total_precipitation:.1f}mm，共有 {rainy_days} 个降水日。")
            
        if not summary_parts:
            return "数据中缺少可分析的关键气象指标。"
            
        return " ".join(summary_parts)

    def generate_insights_report(self, df, use_openai=False, custom_prompt=None):
        """
        生成关于气象数据的洞察报告。
        如果配置了OpenAI API且use_openai为True，则尝试调用GPT生成。
        否则，使用基于模板的报告。
        :param df: 输入的DataFrame。
        :param use_openai: 是否尝试使用OpenAI API。
        :param custom_prompt: (可选) 用户提供的自定义OpenAI prompt。
        :return: 文本格式的洞察报告。
        """
        if df.empty:
            return "数据为空，无法生成洞察报告。"

        basic_summary = self.get_data_summary(df)
        anomalies_df, anomaly_info = self.detect_anomalies(df.copy()) # 使用副本以避免修改原df

        report = f"## 气象数据AI分析报告\n\n"
        report += f"### 1. 数据摘要\n{basic_summary}\n\n"
        
        report += f"### 2. 异常天气分析\n"
        if anomaly_info:
            report += f"分析了 {anomaly_info.get('total_points_analyzed', 'N/A')} 条数据记录。\n"
        if not anomalies_df.empty:
            report += f"检测到 {len(anomalies_df)} 个潜在的异常天气日。主要特征表现为极端温度、湿度或降水。\n"
            report += "例如，日期 " + anomalies_df['date'].dt.strftime('%Y-%m-%d').head(2).str.cat(sep=', ') + " 等可能存在异常。\n"
        elif anomaly_info and "message" in anomaly_info and "Not enough data" in anomaly_info["message"]:
            report += "数据量不足，无法进行有效的异常检测。\n"
        elif anomaly_info and "message" in anomaly_info and "Error" in anomaly_info["message"]:
            report += f"异常检测过程中发生错误: {anomaly_info['message']}\n"
        else:
            report += "根据当前分析，未检测到显著的异常天气模式。\n"
        
        # OpenAI 集成部分 (占位)
        if use_openai and self.openai_api_key:
            # 此处为调用OpenAI API的示例逻辑，实际使用需要安装openai库并配置好API密钥
            # prompt = f"基于以下气象数据摘要和异常分析，生成一份专业的洞察报告：\n摘要：{basic_summary}\n异常：{anomalies_df.to_string() if not anomalies_df.empty else '无显著异常'}\n请分析潜在的趋势、模式和值得注意的方面。"
            # if custom_prompt:
            #    prompt = custom_prompt
            # try:
            #     response = openai.Completion.create(
            #         engine="text-davinci-003", # 或其他合适的模型
            #         prompt=prompt,
            #         max_tokens=300
            #     )
            #     ai_insight = response.choices[0].text.strip()
            #     report += f"\n### 3. OpenAI 智能洞察\n{ai_insight}\n"
            # except Exception as e:
            #     report += f"\n### 3. OpenAI 智能洞察\n调用OpenAI API失败: {e}\n"
            report += f"\n### 3. OpenAI 智能洞察\n(OpenAI集成占位符：若配置API Key并启用，此处将显示GPT生成的洞察。)\n"
        else:
            report += f"\n### 3. 智能洞察\n(AI洞察功能当前使用模板生成。配置OpenAI API可获取更深入分析。)\n"
            # 添加一些基于规则的简单洞察
            if 'temperature' in df.columns and df['temperature'].mean() > 25:
                report += "- 夏季平均温度较高，可能存在热浪风险。\n"
            if 'precipitation' in df.columns and df[df['precipitation'] > 20].shape[0] > 3:
                 report += "- 存在数个强降水日，需关注可能的内涝风险。\n"

        report += "\n--- \n报告生成时间: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        return report

    def predict_future_weather(self, df, days_to_predict=7):
        """
        预测未来天气 (占位符)。
        :param df: 输入的历史数据DataFrame。
        :param days_to_predict: 需要预测的天数。
        :return: 预测结果或提示信息。
        """
        # 实际的预测模型会复杂得多，这里仅作占位
        # 例如，可以使用ARIMA, Prophet等时序模型
        return f"未来 {days_to_predict} 天的天气预测功能正在开发中。敬请期待！"

if __name__ == "__main__":
    # 创建一个简单的数据样本进行测试
    dates = pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', 
                            '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10'])
    data = {
        'date': dates,
        'temperature': [5, 6, 55, 7, 8, 9, 4, 6, 7, 60], # 55 和 60 是异常值
        'humidity': [60, 62, 61, 63, 20, 65, 60, 58, 59, 98], # 20 和 98 是异常值
        'precipitation': [0, 0, 1, 0, 5, 0, 0, 2, 0, 30], # 30 是异常值
        'wind_speed': [10,12,11,13,10,9,14,10,11,12]
    }
    sample_df = pd.DataFrame(data)

    # 初始化分析器 (如果需要使用OpenAI，传入API Key)
    # api_key = os.getenv("OPENAI_API_KEY") # 建议从环境变量读取
    # analyzer = WeatherAIAnalyzer(openai_api_key=api_key)
    analyzer = WeatherAIAnalyzer()

    print("--- 异常检测测试 ---")
    anomalies, info = analyzer.detect_anomalies(sample_df.copy()) # 使用副本
    if not anomalies.empty:
        print("检测到的异常数据:")
        print(anomalies[['date', 'temperature', 'humidity', 'precipitation', 'is_anomaly', 'anomaly_score']])
    else:
        print("未检测到异常或检测出错。")
    print(f"异常检测信息: {info}")
    print("\n--- 数据摘要测试 ---")
    summary = analyzer.get_data_summary(sample_df)
    print(summary)

    print("\n--- 洞察报告测试 (模板) ---")
    report_template = analyzer.generate_insights_report(sample_df.copy()) # 使用副本
    print(report_template)

    # print("\n--- 洞察报告测试 (尝试OpenAI，如果配置了API KEY) ---")
    # report_openai = analyzer.generate_insights_report(sample_df.copy(), use_openai=True)
    # print(report_openai)

    print("\n--- 未来天气预测测试 ---")
    prediction = analyzer.predict_future_weather(sample_df)
    print(prediction)
    
    print("\nAI分析模块基本功能测试完成。")
