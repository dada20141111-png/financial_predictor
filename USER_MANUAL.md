# 金融预测 AI 系统用户手册
# Financial Predictor AI User Manual

本手册旨在帮助您全面了解并使用本系统。
This manual is designed to help you understand and use the system comprehensively.

---

## 1. 总体概括 (General Overview)

**项目简介 (Introduction)**
Financial Predictor AI 是一个集成了机器学习 (XGBoost) 和深度学习 (MLP) 的智能金融预测系统。它不仅关注传统的 K 线数据，还融合了宏观经济指标（如黄金、原油、恐慌指数）和市场舆情（新闻情绪），为您提供多维度的行情分析。

Financial Predictor AI is an intelligent system integrating Machine Learning (XGBoost) and Deep Learning (MLP). It goes beyond traditional candlesticks by incorporating Macroeconomic indicators (Gold, Oil, VIX) and Market Sentiment, providing multi-dimensional analysis.

**核心价值 (Core Value)**
-   **数据驱动**: 整合 Yahoo Finance 及 Google News 数据。
-   **双模预测**: 提供树模型 (XGBoost) 和神经网络 (MLP) 两种视角。
-   **模拟交易**: 内置全功能模拟交易系统，零风险验证策略。
-   **实盘就绪**: 支持从模拟无缝切换至实盘交易 (Live Trading)。

---

## 2. 功能介绍 (Feature Introduction)

### 2.1 预测引擎 (Prediction Engine)
-   **多模型支持 (Multi-Model)**:
    -   `XGBoost`: 擅长捕捉非线性关系，训练速度快。
    -   `MLP (Neural Network)`: 深度学习感知机，擅长处理复杂模式。
-   **自动调优 (Auto-Tuning) (New)**: 使用 `Optuna` 自动寻找最佳参数（需使用 CLI 模式）。

### 2.2 宏观感知 (Macro Awareness)
系统自动拉取以下指标作为辅助特征：
-   **贵金属**: 黄金 (Gold), 白银 (Silver), 铜 (Copper)
-   **能源/农产品**: 原油 (Oil), 玉米 (Corn), 大豆 (Soybeans), 小麦 (Wheat)
-   **市场状态**: 10年期美债收益率 (TNX), 恐慌指数 (VIX)

### 2.3 情绪分析 (Sentiment Analysis) (New)
-   **实时舆情**: 抓取 Google News 最新标题。
-   **NLP 评分**: 计算情绪分 (-1.0 极度悲观 ~ +1.0 极度乐观) 及市场心情 (Mood)。

### 2.4 交易执行 (Execution & Trading)
-   **三档模式 (3-Mode Switch)**:
    1.  **Mock (模拟)**: 本地记账，无网络请求，绝对安全。
    2.  **Testnet (测试网)**: 连接交易所 Sandbox 环境。
    3.  **Live (实盘)**: 真实资金交易（带二次确认保护）。
-   **策略功能**: 支持止损 (Stop-Loss) 和止盈 (Take-Profit) 设置。

---

## 3. 详细使用说明 (Detailed Usage Instructions)

### 3.1 快速启动 (Quick Start)
双击文件夹中的 `FinancialPredictorAI.exe` 即可启动图形化仪表盘。
Double-click `FinancialPredictorAI.exe` to launch the Dashboard.

### 3.2 仪表盘界面说明 (Dashboard Interface)

#### **侧边栏 (Sidebar)**
-   **Asset Selection**: 选择交易对 (如 BTC-USD)。
-   **Model Settings**:
    -   `Training Window`: 训练数据回溯天数 (默认 730天)。
    -   `Model Type`: 选择 XGBoost 或 MLP。
-   **Trading Controls**:
    -   `Position Sizing`: 设置模拟交易的仓位大小 (如 0.1 BTC)。
    -   `Stop Loss / Take Profit`: 设置止损止盈百分比。
    -   `Buy / Sell Buttons`: 手动下单按钮。

#### **主区域 (Main Area)**
1.  **Price Chart**: 显示资产价格走势及布林带 (Bollinger Bands)。
2.  **Macro Correlations**: 热力图展示资产与黄金、原油等的相关性。
3.  **Prediction**:
    -   显示主要预测结果 (Next Day Price)。
    -   显示当前市场情绪 (Market Sentiment)。
4.  **Portfolio Status**: 当前持仓详情及浮动盈亏。
5.  **Trade History**: 历史交易记录列表。

### 3.3 高级功能 (Advanced CLI Usage)
如果您是开发者或高级用户，可以使用命令行 (CMD/PowerShell) 运行更多功能。

**1. 自动训练与调优 (Auto-Tuning)**
```bash
# 开启 Optuna 自动寻找最佳参数
python -m src.main_phase2 --symbol BTC-USD --optimize
```

**2. 切换交易模式 (Switch Trading Modes)**
编辑 `release/.env` 文件：
```ini
# 修改 TRADING_MODE 为 mock, testnet 或 live
TRADING_MODE=mock
```

**3. 配置文件 (Configuration)**
编辑 `src/config.py` 可修改：
-   `MACRO_SYMBOLS`: 添加或删除宏观指标。
-   `DEFAULT_TRAINING_DAYS`: 修改默认训练时长。

---

**常见问题 (FAQ)**
-   **Q: 为什么预测结果没有变化？**
    -   A: 市场数据更新频率为每日收盘。盘中波动不会立即改变基于日线的模型预测。
-   **Q: .exe 启动报错？**
    -   A: 请确保 `.env` 文件和 `_internal` 文件夹与 `.exe` 在同一目录下。
