# 智能气象数据分析平台 - 用户指南

## 1. 引言

欢迎使用智能气象数据分析平台！本项目旨在提供一个集数据处理、可视化和AI智能分析于一体的气象数据分析解决方案。本指南将引导您完成项目的安装、配置和使用。

## 2. 先决条件

在开始之前，请确保您的系统已安装以下软件：
- Python (推荐版本 3.9 或更高)
- Conda (用于环境管理)
- Git (用于版本控制)

## 3. 安装与配置

### 3.1. 克隆仓库
首先，使用Git克隆项目仓库到您的本地计算机：
```bash
git clone https://github.com/ABEL-L76/gaolab.git
cd gaolab
```

### 3.2. 创建并激活Conda环境
项目依赖定义在 `environment.yml` 文件中。使用以下命令创建并激活Conda环境：
```bash
conda env create -f environment.yml
conda activate weather-analysis-enhanced 
```
*(注意：环境名称 `weather-analysis-enhanced` 以 `environment.yml` 中定义的为准)*

### 3.3. (可选) OpenAI API Key 配置
如果需要使用基于OpenAI GPT的智能洞察功能，您需要配置OpenAI API Key：
1. 获取您的OpenAI API Key。
2. 在项目根目录创建一个名为 `.env` 的文件。
3. 在 `.env` 文件中添加以下行，并替换 `YOUR_API_KEY` 为您的真实密钥：
   ```
   OPENAI_API_KEY="YOUR_API_KEY"
   ```
   **注意**: `.env` 文件已被添加到 `.gitignore`，不会被提交到版本库。

## 4. 项目结构

项目主要目录结构如下：
- `app/`: 包含Streamlit Web应用 (`streamlit_app.py`)。
- `data/`: 用于存放原始数据 (`raw/`) 和处理后数据 (`processed/`) (默认不提交具体数据文件到Git)。
- `docs/`: 包含项目文档，如本用户指南。
- `notebooks/`: 包含Jupyter Notebooks或Quarto文档 (`enhanced_analysis.qmd`)，用于文学化编程和报告。
- `src/`: 包含核心Python模块：
    - `data_processor.py`: 数据生成、清洗和预处理。
    - `visualizer.py`: 数据可视化函数。
    - `ai_analyzer.py`: AI分析功能，如异常检测、报告生成。
    - `main.py`: 项目主程序入口（如果适用）。
- `results/`: 存放分析结果，如图片、报告等 (默认不提交具体结果文件到Git)。
- `environment.yml`: Conda环境配置文件。
- `requirements.txt`: pip依赖文件 (可通过conda环境导出)。
- `README.md`: 项目概览和快速开始。
- `.gitignore`: 指定Git忽略的文件和目录。

## 5. 运行平台

### 5.1. 运行Streamlit Web应用
确保您的Conda环境已激活。在项目根目录下执行以下命令：
```bash
streamlit run app/streamlit_app.py
```
这将在您的默认浏览器中打开一个本地Web服务 (通常是 `http://localhost:8501`)，您可以交互式地浏览和分析数据。

### 5.2. 运行数据处理/分析脚本 (如果适用)
如果项目包含批处理脚本 (如 `src/main.py`)，您可以直接运行它：
```bash
python src/main.py
```

## 6. 使用Streamlit Web应用

Web应用提供了友好的用户界面进行气象数据分析：
- **导航菜单 (侧边栏)**: 切换不同的分析页面（数据概览、可视化分析、AI智能分析、项目介绍）。
- **数据控制**: 重新生成示例数据。
- **数据筛选**: 根据日期范围、季节等筛选数据。
- **数据概览页面**: 显示基本统计指标、数据样本表格和下载选项。
- **可视化分析页面**: 提供多种图表类型（温度趋势、季节对比、相关性热力图等）进行探索性数据分析。
- **AI智能分析页面**:
    - **异常检测**: 自动识别数据中的异常天气情况。
    - **智能报告生成**: (若配置OpenAI API) 生成基于AI的分析报告，或使用模板报告。
    - **预测分析**: (占位符) 未来可扩展天气预测功能。

## 7. 文学化编程报告

项目包含一个使用Quarto编写的文学化编程报告 `notebooks/enhanced_analysis.qmd`。
- **查看/渲染**:
    - **VS Code**: 如果安装了Quarto扩展，可以直接在VS Code中打开并渲染。
    - **命令行**: 安装 [Quarto CLI](https://quarto.org/docs/get-started/) 后，在项目根目录下运行：
      ```bash
      quarto render notebooks/enhanced_analysis.qmd
      ```
      这会生成一个HTML版本的报告。

## 8. 贡献指南

我们欢迎对本项目的贡献！请遵循以下步骤：
1.  Fork主仓库 (`ABEL-L76/gaolab`) 到您自己的GitHub账户。
2.  将您的Fork克隆到本地。
3.  添加主仓库为上游远程仓库 (`git remote add upstream https://github.com/ABEL-L76/gaolab.git`)。
4.  基于最新的主分支 (`main`) 创建一个新的特性分支 (`git checkout -b feature/your-new-feature`)。
5.  进行代码修改和开发。
6.  提交您的更改 (`git commit -am 'Add some feature'`)。
7.  将您的特性分支推送到您的Fork仓库 (`git push origin feature/your-new-feature`)。
8.  在GitHub上向主仓库的 `main` 分支发起Pull Request。
9.  等待代码审查和合并。

## 9. 故障排除

- **模块导入错误**: 确保您已正确激活Conda环境 (`conda activate weather-analysis-enhanced`)。检查 `sys.path` 配置是否正确指向 `src` 目录。
- **Streamlit命令未找到**: 确认Streamlit已在Conda环境中安装，并且环境已激活。
- **OpenAI API错误**: 检查您的API Key是否正确配置在 `.env` 文件中，以及网络连接是否正常。

如有其他问题，请在项目的GitHub Issues中提出。
