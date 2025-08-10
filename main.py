# coding: utf-8
import json
from flask import Flask, request, jsonify
from lunarcalendar import Converter, Solar, Lunar
from datetime import datetime
from typing import Dict, Any, Tuple, Union

app = Flask(__name__)

# 常量定义
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

BAGUA_SYMBOLS = {
    1: "\u2630",  # ☰
    2: "\u2637",  # ☷
    3: "\u2633",  # ☳
    4: "\u2636",  # ☶
    5: "\u2632",  # ☲
    6: "\u2635",  # ☵
    7: "\u2631",  # ☱
    8: "\u2634"   # ☴
}


# 实现用户验证
def get_user_mapping():
    """读取用户数据，返回用户名到令牌的映射字典"""
    user_map = {}
    with open('db.txt', mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                token, username = line.split(',', 1)
                user_map[username] = token
    return user_map

# 全局变量
USER_MAPPING = get_user_mapping()


# 辅助函数
def validate_request(data: Dict[str, Any]) -> Union[None, Tuple[Dict[str, str], int]]:
    """验证请求是否有效，检查用户名和令牌的对应关系"""
    if not data:
        return {"error": "缺少JSON数据"}, 400
    
    token = data.get('token')
    username = data.get('username')
    
    if not token or not username:
        return {'error': "缺少token或username参数"}, 400
    
    # 检查用户名是否存在
    if username not in USER_MAPPING:
        return {'error': "用户名不存在"}, 401
    
    # 验证令牌是否匹配该用户名
    if token != USER_MAPPING[username]:
        return {'error': "令牌与用户名不匹配"}, 401
    
    return None

def validate_query_params():
    """验证URL查询参数中的用户名和令牌"""
    token = request.args.get('token')
    username = request.args.get('username')
    
    if not token or not username:
        return {'error': "缺少token或username参数"}, 400
    
    if username not in USER_MAPPING:
        return {'error': "用户名不存在"}, 401
    
    if token != USER_MAPPING[username]:
        return {'error': "令牌与用户名不匹配"}, 401
    
    return None

def calculate_mod_value(value: int, modulus: int) -> int:
    """计算模值，处理0值情况"""
    mod_value = value % modulus
    return modulus if mod_value == 0 else mod_value

def get_shichen_index(hour: int) -> int:
    """计算时辰对应的索引"""
    return (hour // 2) % 12

# 路由处理
@app.route('/test')
def test_connection() -> str:
    """测试连通性"""
    return '服务运行正常'

@app.route('/WanNianLi', methods=['POST'])
def perpetual_calendar() -> Tuple[Dict[str, Any], int]:
    """
    万年历转换接口
    输入: JSON {token, username, year, month, day}
    输出: 农历日期信息
    """
    data = request.get_json()
    if error := validate_request(data):
        return error
    
    try:
        year, month, day = data['year'], data['month'], data['day']
        solar = Solar(year=year, month=month, day=day)
        lunar = Converter.Solar2Lunar(solar=solar)
        
        # 计算农历年干支
        gan_index = (year - 4) % 10
        zhi_index = (year - 4) % 12
        lunar_year = TIANGAN[gan_index] + DIZHI[zhi_index]
        
        return {
            '农历年': lunar_year,
            'year_index': zhi_index + 1,
            '农历月': lunar.month,
            '农历日': lunar.day,
            '是否闰月': lunar.isleap,
        }, 200
    
    except KeyError as e:
        return {'error': f'缺少必要参数: {str(e)}'}, 400
    except Exception as e:
        return {'error': f'处理错误: {str(e)}'}, 500

@app.route('/ShiChen')
def hourly_period() -> Tuple[Dict[str, Any], int]:
    """
    时辰转换接口
    输入: URL参数 ?username=用户名&token=令牌&hour=小时数
    输出: 时辰信息
    """
    try:
        # 验证查询参数
        if error := validate_query_params():
            return error
        
        hour_str = request.args.get('hour')
        if not hour_str:
            return {"error": "缺少小时参数"}, 400
        
        hour = int(hour_str)
        if not (0 <= hour <= 23):
            return {"error": "小时值必须在0-23之间"}, 416
        
        index = get_shichen_index(hour)
        if index == 11:
            index = 0
        shi_chen = DIZHI[index] + '时'
        
        return {
            "shichen": shi_chen,
            "index": index + 1
        }, 200
    
    except ValueError:
        return {"error": "无效的小时格式，必须是整数"}, 400
    except Exception as e:
        return {'error': f'处理错误: {str(e)}'}, 500

@app.route('/MeiHuaZhan', methods=['POST'])
def plum_blossom_divination() -> Tuple[Dict[str, Any], int]:
    """
    梅花易数占卜接口
    输入: JSON {token, username, first_num, second_num}
    输出: 卦象信息
    """
    data = request.get_json()
    if error := validate_request(data):
        return error
    
    try:
        first_num = data['first_num']
        second_num = data['second_num']
        
        # 计算上卦
        upper = calculate_mod_value(first_num, 8)
        # 计算下卦
        lower = calculate_mod_value(second_num, 8)
        # 计算动爻
        moving_line = calculate_mod_value(first_num + second_num, 6)
        
        return {
            '上卦': BAGUA_SYMBOLS[upper],
            '下卦': BAGUA_SYMBOLS[lower],
            '动爻': moving_line,
            '注意': '本接口只能算出卦象和动爻，若要解析卦象请翻阅书籍。'
        }, 200
    
    except KeyError as e:
        return {'error': f'缺少必要参数: {str(e)}'}, 400
    except Exception as e:
        return {'error': f'处理错误: {str(e)}'}, 500

if __name__ == '__main__':
    app.run(debug=True)