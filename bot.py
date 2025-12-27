import yfinance as yf
import pandas_ta as ta
import requests
import schedule
import time

# --- 配置区域 ---
TELEGRAM_TOKEN = '你的_API_TOKEN_粘贴在这里'
CHAT_ID = '你的_CHAT_ID_粘贴在这里'
STOCKS = ['AAPL', 'TSLA', 'NVDA', 'BABA'] # 你关注的股票列表
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70 # 超买阈值
RSI_OVERSOLD = 30   # 超卖阈值

# 发送 Telegram 消息的函数
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
        print(f"消息已发送: {message}")
    except Exception as e:
        print(f"发送失败: {e}")

# 核心分析函数
def check_market():
    print(f"正在扫描市场... {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    for symbol in STOCKS:
        try:
            # 获取最近的数据 (1小时级别，适合短线监测)
            df = yf.download(symbol, period="5d", interval="1h", progress=False)
            
            if df.empty:
                continue

            # 计算 RSI
            # pandas_ta 会自动添加一列 'RSI_14'
            df.ta.rsi(length=RSI_PERIOD, append=True)
            
            # 获取最新的 RSI 值
            current_rsi = df[f'RSI_{RSI_PERIOD}'].iloc[-1]
            current_price = df['Close'].iloc[-1]

            # 判断逻辑
            msg = ""
            if current_rsi < RSI_OVERSOLD:
                msg = f"🟢 【买入信号】\n股票: {symbol}\n价格: ${current_price:.2f}\nRSI: {current_rsi:.2f} (超卖)"
            elif current_rsi > RSI_OVERBOUGHT:
                msg = f"🔴 【卖出信号】\n股票: {symbol}\n价格: ${current_price:.2f}\nRSI: {current_rsi:.2f} (超买)"
            
            # 如果有信号，发送推送
            if msg:
                send_telegram_message(msg)
                
        except Exception as e:
            print(f"分析 {symbol} 时出错: {e}")

# --- 调度区域 ---
# 每 1 小时运行一次 check_market
schedule.every(1).hours.do(check_market)

# 启动提示
print("🤖 股票监控机器人已启动...")
send_telegram_message("🤖 机器人上线：开始监控 RSI 数据")

# 保持脚本运行
while True:
    schedule.run_pending()
    time.sleep(1)