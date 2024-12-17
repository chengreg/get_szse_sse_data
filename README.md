# 沪深股市数据获取工具

这个项目提供了用于获取上海证券交易所（SSE）和深圳证券交易所（SZSE）市场数据的Python工具。

## 功能特点

- 支持获取上交所数据：
  - A股市场数据
  - B股市场数据
  - 基金数据
  - 指数数据
- 支持获取深交所数据：
  - 股票数据
  - 基金数据
  - 债券数据
  - 债券回购数据
  - 期权数据
  - 指数数据

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/chengreg/get_szse_sse_data.git
cd get_szse_sse_data
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 获取上交所数据

```python
from sse import SSEMarketData, get_sse_market_data

# 方法1：使用便捷函数
df = get_sse_market_data('A股')  # 可选：'A股', 'B股', '基金', '指数'

# 方法2：使用类
sse = SSEMarketData()
df = sse.get_market_data('A股')
filename, filepath = sse.save_to_csv(df, 'A股')
```

### 获取深交所数据

```python
from szse import SZSEMarketData, get_szse_market_data

# 方法1：使用便捷函数
df = get_szse_market_data('股票')  # 可选：'股票', '基金', '债券', '债券回购', '期权', '指数'

# 方法2：使用类
szse = SZSEMarketData()
df = szse.get_market_data('股票')
filename, filepath = szse.save_to_csv(df, '股票')
```

## 数据来源

- 上交所数据来源：https://www.sse.com.cn/market/price/report/
- 深交所数据来源：https://www.szse.cn/market/trend/index.html

## 注意事项

1. 数据仅供参考，实际交易请以交易所官方数据为准
2. 请遵守交易所的数据使用规范
3. 建议在非交易时段获取数据，避免频繁访问影响交易所服务器

## License

MIT License
