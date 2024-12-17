#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""--------------------------------------------------------------------------
@FileName:		sse.py
@Author:		Chen GangQiang
@Version:		v1.0.0
@CreationDate:	2024/12/17 21:21
@Update Date:	2024/12/17 21:21
@Description:	上海证券交易所数据获取模块
@History:
 <author>        <time>         <version>   <desc>
 ChenGangQiang  2024/12/17 21:21 1.0.0       build this module
-----------------------------------------------------------------------------
* Copyright @ 陈钢强 2024. All rights reserved.
--------------------------------------------------------------------------"""
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import pandas as pd
from datetime import datetime
import os
from typing import Optional, Dict, Union, List
import json
import random


class SSEMarketData:
    """上海证券交易所市场行情数据获取类"""
    # https://www.sse.com.cn/market/price/report/
    
    BASE_URL = "https://yunhq.sse.com.cn:32042"
    
    # 定义市场类型和对应的URL路径
    MARKET_TYPES = {
        "A股": {"path": "/v1/sh1/list/exchange/equity", "name_field": "name"},
        "B股": {"path": "/v1/shb1/list/exchange/all", "name_field": "name"},
        "基金": {"path": "/v1/sh1/list/exchange/fwr", "name_field": "cpxxextendname"},
        "指数": {"path": "/v1/sh1/list/exchange/index", "name_field": "name"}
    }
    
    def __init__(self):
        """初始化方法"""
        self.download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.sse.com.cn/',
            'Host': 'yunhq.sse.com.cn:32042',
            'Origin': 'https://www.sse.com.cn'
        }

    def get_market_data(self, market_type: str) -> Optional[pd.DataFrame]:
        """
        获取指定类型的市场数据
        
        Args:
            market_type: 市场类型，可选值：'A股'、'B股'、'基金'、'指数'
            
        Returns:
            pd.DataFrame: 市场数据，如果发生错误则返回None
        """
        if market_type not in self.MARKET_TYPES:
            raise ValueError(f"不支持的市场类型: {market_type}. 支持的类型: {list(self.MARKET_TYPES.keys())}")

        try:
            market_info = self.MARKET_TYPES[market_type]
            url = f"{self.BASE_URL}{market_info['path']}"
            name_field = market_info['name_field']
            
            # 选择的字段
            fields = [
                'code', name_field, 'open', 'high', 'low', 'last',
                'prev_close', 'chg_rate', 'volume', 'amount',
                'tradephase', 'change', 'amp_rate', 'cpxxsubtype'
            ]
            if market_type == "基金":
                fields[1] = "cpxxextendname"  # 基金使用不同的名称字段
            
            params = {
                'callback': f'jsonpCallback{random.randint(10000000, 99999999)}',
                'select': ','.join(fields),
                'order': '',
                'begin': 0,
                'end': 5000,  # 设置较大的数值以获取所有数据
                '_': int(datetime.now().timestamp() * 1000)
            }
            
            # 发送请求获取数据
            response = requests.get(url, params=params, headers=self.headers, verify=False)
            
            if response.status_code != 200:
                raise Exception(f"请求失败，状态码: {response.status_code}")
            
            # 处理jsonp响应
            text = response.text
            json_str = text[text.index('(') + 1:text.rindex(')')]
            data = json.loads(json_str)
            
            # 提取数据并创建DataFrame
            if 'list' in data:
                df = pd.DataFrame(data['list'], columns=fields)
                
                # 重命名列
                column_mapping = {
                    'code': '证券代码',
                    name_field: '证券名称',
                    'open': '开盘价',
                    'high': '最高价',
                    'low': '最低价',
                    'last': '最新价',
                    'prev_close': '昨收价',
                    'chg_rate': '涨跌幅',
                    'volume': '成交量',
                    'amount': '成交额',
                    'tradephase': '交易状态',
                    'change': '涨跌额',
                    'amp_rate': '振幅',
                    'cpxxsubtype': '证券类型'
                }
                df.rename(columns=column_mapping, inplace=True)
                
                # 处理数据格式
                df['证券代码'] = df['证券代码'].astype(str).str.zfill(6)
                for col in ['开盘价', '最高价', '最低价', '最新价', '昨收价', '涨跌幅', '涨跌额', '振幅']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 添加市场类型和交易日期列
                df.insert(0, '市场类型', market_type)
                df.insert(1, '交易日期', datetime.now().strftime('%Y-%m-%d'))
                
                return df
            else:
                raise Exception("数据格式不正确")

        except Exception as e:
            print(f"获取{market_type}数据时出现错误: {str(e)}")
            return None

    def get_all_market_data(self) -> List[pd.DataFrame]:
        """
        获取所有市场类型的数据
        
        Returns:
            List[pd.DataFrame]: 所有市场数据的列表
        """
        all_data = []
        for market_type in self.MARKET_TYPES.keys():
            print(f"正在获取{market_type}数据...")
            df = self.get_market_data(market_type)
            if df is not None:
                all_data.append(df)
        return all_data

    def save_to_csv(self, df: pd.DataFrame, data_type: str) -> tuple[Optional[str], Optional[str]]:
        """
        将数据保存为CSV文件
        
        Args:
            df: 要保存的DataFrame数据
            data_type: 数据类型
            
        Returns:
            tuple: (文件名, 文件路径)，如果保存失败则返回(None, None)
        """
        try:
            trade_date = datetime.now().strftime('%Y%m%d')
            csv_filename = f'sse_market_{data_type}_{trade_date}.csv'
            csv_filepath = os.path.join(self.download_path, csv_filename)
            
            df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
            return csv_filename, csv_filepath
        except Exception as e:
            print(f"保存CSV文件时出现错误: {str(e)}")
            return None, None


def get_sse_market_data(market_type: str) -> Optional[pd.DataFrame]:
    """
    获取上交所市场数据的便捷函数
    
    Args:
        market_type: 市场类型，可选值：'A股'、'B股'、'基金'、'指数'
        
    Returns:
        pd.DataFrame: 市场数据，如果发生错误则返回None
    """
    sse = SSEMarketData()
    return sse.get_market_data(market_type)


if __name__ == "__main__":
    # 测试代码
    sse = SSEMarketData()
    
    # 获取并保存每个市场的数据
    for market_type in sse.MARKET_TYPES.keys():
        print(f"\n正在获取{market_type}数据...")
        df = sse.get_market_data(market_type)
        
        if df is not None:
            # 保存数据
            filename, filepath = sse.save_to_csv(df, market_type)
            if filename and filepath:
                print(f"{market_type}数据已保存为CSV格式: {filename}")
                print(f"文件保存路径: {filepath}")
                print(f"数据形状: {df.shape}")
                print(f"列名: {df.columns.tolist()}")
                
                # 显示前5条记录
                print(f"\n{market_type}数据前5条记录:")
                print(df.head().to_string())
            print("-" * 50)