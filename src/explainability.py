import pandas as pd
from typing import Dict, List

# Feature Name Mapping to Chinese
FEATURE_MAP = {
    'RSI': '相对强弱指数 (RSI)',
    'RSI_14': '相对强弱指数 (RSI)',
    'MACD': 'MACD趋势指标',
    'MACD_Signal': 'MACD信号线',
    'MACD_Hist': 'MACD动能柱',
    'BB_Upper': '布林带上轨',
    'BB_Lower': '布林带下轨',
    'BB_Middle': '布林带中轨',
    'SMA_50': '50日均线',
    'SMA_200': '200日均线',
    'Volume': '成交量',
    'Close': '收盘价',
    'Open': '开盘价',
    'High': '最高价',
    'Low': '最低价',
    'ATR': '平均真实波幅 (ATR)',
    'OBV': '能量潮 (OBV)',
    'VIX': '恐慌指数 (VIX)',
    'DXY': '美元指数',
    'US10Y': '10年美债收益率'
}

def generate_explanation(feature_importance: pd.Series, horizon: str, probability: float) -> str:
    """
    Generate a Chinese explanation based on top features and probability.
    
    Args:
        feature_importance: Series of feature importances.
        horizon: 'Day', 'Week', or 'Month'.
        probability: Probability of Rise (0.0 - 1.0).
    """
    
    # 1. Determine Sentiment
    direction = "看涨" if probability > 0.5 else "看跌"
    confidence = abs(probability - 0.5) * 2 # 0.0 - 1.0 scale
    
    conf_str = "中性"
    if confidence > 0.6: conf_str = "极强"
    elif confidence > 0.3: conf_str = "强"
    elif confidence > 0.1: conf_str = "弱"
    
    # 2. Top Features
    top_3 = feature_importance.head(3)
    features_text = []
    
    for name, score in top_3.items():
        # Clean name (remove lag suffixes if any)
        clean_name = name.split('_lag')[0]
        cn_name = FEATURE_MAP.get(clean_name, name)
        features_text.append(f"{cn_name} (权重 {score:.1%})")
        
    features_joined = "、".join(features_text)
    
    # 3. Construct Text
    intro = f"**AI 预测分析 ({horizon})**:\n"
    summary = f"模型当前 **{conf_str}{direction}** (上涨概率 {probability:.1%})。\n\n"
    
    logic = f"**主要驱动因素**:\n本轮预测主要受 {features_joined} 等指标影响。\n"
    
    # Simple rule-based logic elaboration (Placeholder for more complex logic)
    elaboration = ""
    top_feature = top_3.index[0]
    if "RSI" in top_feature:
        elaboration = "相对强弱指数 (RSI) 对短期波动非常敏感，模型可能监测到了超买/超卖信号。"
    elif "MACD" in top_feature:
        elaboration = "MACD 趋势指标显示动能变化，通常预示着趋势的延续或反转。"
    elif "Volume" in top_feature:
        elaboration = "成交量的显著变化通常是价格剧烈波动的前兆。"
    elif "SMA" in top_feature:
        elaboration = "均线系统 (SMA) 指明了长期趋势支撑/阻力位。"
        
    return intro + summary + logic + elaboration
