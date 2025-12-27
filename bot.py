import os
import yfinance as yf
import pandas_ta as ta
import requests

# --- 1. 从 GitHub 环境变量读取配置 ---
TOKEN = os.environ.get('TG_TOKEN')
CHAT_ID = os.environ.get('TG_CHAT_ID')

STOCKS = ['AAPL', 'TSLA', 'NVDA', 'BABA']
RSI_PERIOD = 14

def send_telegram_message(message):
    if not TOKEN or not CHAT_ID:
        print("❌ 错误：无法读取 Token 或 Chat ID，请检查 GitHub Secrets 设置")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
        print(f"消息已发送: {message}")
    except Exception as e:
        print(f"发送失败: {e}")

def check_market():
    print("🚀 开始扫描市场...")
    triggered = False
    
    for symbol in STOCKS:
        try:
            # 获取数据
            df = yf.download(symbol, period="5d", interval="1h", progress=False)
            if df.empty or len(df) < RSI_PERIOD:
                continue

            # 计算 RSI
            rsi_val = ta.rsi(df['Close'], length=RSI_PERIOD).iloc[-1]
            price = df['Close'].iloc[-1]

            msg = ""
            # 判断逻辑
            if rsi_val < 30:
                msg = f"🟢 {symbol} 机会: ${price:.2f} | RSI: {rsi_val:.2f} (超卖)"
            elif rsi_val > 70:
                msg = f"🔴 {symbol} 风险: ${price:.2f} | RSI: {rsi_val:.2f} (超买)"
            
            if msg:
                send_telegram_message(msg)
                triggered = True
                
        except Exception as e:
            print(f"分析 {symbol} 出错: {e}")

    if not triggered:
        print("✅ 扫描完成，无异常信号")

# 只运行一次，不需要 while True
if __name__ == "__main__":
    check_market()
