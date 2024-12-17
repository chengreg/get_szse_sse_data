#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""--------------------------------------------------------------------------
@FileName:		szse.py
@Author:		Chen GangQiang
@Version:		v1.0.0
@CreationDate:	2024/12/17 21:07
@Update Date:	2024/12/17 21:07
@Description:	
@History:
 <author>        <time>         <version>   <desc>
 ChenGangQiang  2024/12/17 21:07 1.0.0       build this module
-----------------------------------------------------------------------------
* Copyright @ 陈钢强 2024. All rights reserved.
--------------------------------------------------------------------------"""
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
import pandas as pd
import requests
from urllib.parse import urljoin
from typing import Optional, Dict, Union


class SZSEMarketData:
    """深圳证券交易所市场行情数据获取类"""
    # https://www.szse.cn/market/trend/index.html
    
    BASE_URL = "https://www.szse.cn"
    MARKET_TYPES = {
        "股票": "1",
        "基金": "2",
        "债券": "3",
        "债券回购": "4",
        "期权": "6",
        "指数": "7"
    }

    def __init__(self):
        """初始化方法"""
        self.download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    def get_market_data(self, market_type: str) -> Optional[pd.DataFrame]:
        """
        获取指定类型的市场数据
        
        Args:
            market_type: 市场类型，可选值：'股票'、'基金'、'债券'、'债券回购'、'期权'、'指数'
            
        Returns:
            pd.DataFrame: 市场数据，如果发生错误则返回None
        """
        if market_type not in self.MARKET_TYPES:
            raise ValueError(f"不支持的市场类型: {market_type}. 支持的类型: {list(self.MARKET_TYPES.keys())}")

        try:
            # 获取当前日期
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # 构建API URL
            api_path = f"/api/report/ShowReport"
            params = {
                "SHOWTYPE": "xlsx",
                "CATALOGID": "1815_stock_snapshot",
                "TABKEY": f"tab{self.MARKET_TYPES[market_type]}",
                "txtBeginDate": current_date,
                "txtEndDate": current_date,
                "archiveDate": "2022-12-01",
                "random": str(time.time())
            }
            
            # 构建完整URL
            url = urljoin(self.BASE_URL, api_path)
            
            # 发送请求下载文件
            response = requests.get(url, params=params)
            if response.status_code != 200:
                raise Exception(f"下载失败，状态码: {response.status_code}")
            
            # 保存临时Excel文件
            temp_file = os.path.join(self.download_path, f'temp_{market_type}.xlsx')
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            # 读取Excel文件并转换为DataFrame
            df = pd.read_excel(temp_file)
            
            # 删除临时Excel文件
            os.remove(temp_file)
            
            return df

        except Exception as e:
            print(f"获取{market_type}数据时出现错误: {str(e)}")
            return None

    def save_to_csv(self, df: pd.DataFrame, market_type: str) -> tuple[Optional[str], Optional[str]]:
        """
        将数据保存为CSV文件
        
        Args:
            df: 要保存的DataFrame数据
            market_type: 市场类型
            
        Returns:
            tuple: (文件名, 文件路径)，如果保存失败则返回(None, None)
        """
        try:
            trade_date = datetime.now().strftime('%Y%m%d')
            csv_filename = f'szse_market_trend_{market_type}_{trade_date}.csv'
            csv_filepath = os.path.join(self.download_path, csv_filename)
            
            df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
            return csv_filename, csv_filepath
        except Exception as e:
            print(f"保存CSV文件时出现错误: {str(e)}")
            return None, None


def get_szse_market_data(market_type: str) -> Optional[pd.DataFrame]:
    """
    获取深交所市场数据的便捷函数
    
    Args:
        market_type: 市场类型，可选值：'股票'、'基金'、'债券'、'债券回购'、'期权'、'指数'
        
    Returns:
        pd.DataFrame: 市场数据，如果发生错误则返回None
    """
    szse = SZSEMarketData()
    return szse.get_market_data(market_type)


if __name__ == "__main__":
    # 测试代码
    szse = SZSEMarketData()
    
    # 测试所有市场类型
    for market_type in szse.MARKET_TYPES.keys():
        print(f"开始获取{market_type}数据...")
        
        # 获取数据
        df = szse.get_market_data(market_type)
        
        if df is not None:
            # 保存为CSV
            filename, filepath = szse.save_to_csv(df, market_type)
            if filename and filepath:
                print(f"{market_type}数据已下载并转换为CSV格式: {filename}")
                print(f"文件保存路径: {filepath}")
                # 显示数据的基本信息
                print(f"数据形状: {df.shape}")
                print(f"列名: {df.columns.tolist()}")
        print("-" * 50)
