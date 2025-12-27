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
        print("❌ 错误：无法读取 Token 或 Chat ID")
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
            
            # 检查数据是否为空
            if df.empty or len(df) < RSI_PERIOD:
                print(f"⚠️ {symbol} 数据不足，跳过")
                continue

            # 计算 RSI
            rsi_series = ta.rsi(df['Close'], length=RSI_PERIOD)
            
            # --- 关键修复：检查 RSI 是否计算成功 ---
            if rsi_series is None:
                print(f"⚠️ {symbol} RSI 计算失败 (可能是数据兼容性问题)")
                continue

            # 获取最新值 (安全读取)
            rsi_val = rsi_series.iloc[-1]
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
            else:
                print(f"{symbol} 正常 - 现价: ${price:.2f}, RSI: {rsi_val:.2f}")
                
        except Exception as e:
            print(f"❌ 分析 {symbol} 时发生未知错误: {e}")

    if not triggered:
        print("✅ 扫描完成，无异常信号")

if __name__ == "__main__":
    check_market()
