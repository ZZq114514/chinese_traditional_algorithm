# 万年历、时辰转换与梅花易数API服务源代码

这是一个基于Flask的API服务，提供万年历转换、时辰转换和梅花易数占卜功能。服务使用Python编写，整合了农历转换和传统占卜算法。

## 功能概述
1. **万年历转换**：将公历日期转换为农历日期
2. **时辰转换**：将24小时制时间转换为传统时辰
3. **梅花易数占卜**：基于数字起卦法生成卦象

## 安装与运行

### 需要的前提
* Python 3.7+
* pip包管理器

### 安装步骤
1. 克隆仓库
  ```
  在终端输入以下指令
  git clone https://github.com/yourusername/chinese-calendar-api.git
  cd chinese-calendar-api
  ```
2. 安装依赖
    ```
    在终端输入以下指令
    pip install flask lunarcalendar
    ```
3. 运行服务
    ```
    在终端输入以下指令
    python main.py
    ```
然后终端就会出现像以下信息就说明服务开始运行
```
 Serving Flask app 'main'
  Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
  Running on http://127.0.0.1:5000
Press CTRL+C to quit
  Restarting with stat
  Debugger is active!
  Debugger PIN: 850-678-651
```
如果想结束运行就在终端中输入`^C`

服务将在默认端口5000启动：`http://127.0.0.1:5000`

# 接口文档

## 接口说明
### 1.测试连通性
* **URL:** `/test`
* **方法:** GET
* **请求参数:** 无
* **响应:**
    ```
    "test"
    ```
### 2.万年历
* **URL:** `/WanNianLi`
* **方法:** POST
* **请求参数(JSON):**
    ```
  {
  "username":"您的用户名"
  "token": "您的API密钥",
  "year": 2023,
  "month": 5,
  "day": 15
  }
    ```
* **响应（例子）:**
    ```
  {
  "农历年": "癸卯",
  "year_index": 4,
  "农历月": 3,
  "农历日": 26,
  "是否闰月": false
  }
    ```
### 3.时辰转换
* **URL:** `/ShiChen`
* **方法:** GET
* **请求参数:**
    `hour`:当前小时（0-23）
    `token`:API密钥
* **示例请求:**
    ```
    http://127.0.0.1:5000/ShiChen?hour=14&token=your_token&username=您的用户名
    ```
* **响应:**
    ```
  {
  "shichen": "未时",
  "Arabic": 8
  }
    ```
### 4.梅花易数
* **URL:** `/MeiHuaZhan`
* **方法:** POST
* **请求参数 (JSON):**
    ```
  {
  "username":"您的用户名"
  "token": "您的API密钥",
  "first_num": 15,
  "second_num": 7
  }
    ```
* **响应:**
    ```
  {
  "上卦": "☶",
  "下卦": "☷",
  "动爻": 4,
  "注意": "本接口只能算出卦象和动爻，若要解析卦象请翻阅书籍。"
  }
    ```

## 错误处理

所有接口在以下情况会返回错误
* 缺少 JSON 数据：`400 Bad Request`
* 缺少 API token：`401 Unauthorized`
* 时辰参数超出范围：`416 Range Not Satisfiable`

## 八卦符号对照表
| 数字 | 八卦符号 | Unicode |
| ---- | -------- | ------- |
| 1    | ☰       | \u2630  |
| 2    | ☷       | \u2637  |
| 3    | ☳       | \u2633  |
| 4    | ☶       | \u2636  |
| 5    | ☲       | \u2632  |
| 6    | ☵       | \u2635  |
| 7    | ☱       | \u2631  |
| 8    | ☴       | \u2634  |

## 注意事项
1. 所有功能接口都需要有效的 API token
2. 时辰计算规则：
    * 每2小时为一个时辰
    * 23:00-1:00 为子时
    * 1:00-3:00 为丑时，依此类推
3. 梅花易数起卦规则：
    * 数字大于8时取模8（余数为0时取8）
    * 动爻计算：两数之和大于6时取模6（余数为0时取6）
4. 如果将此服务部署与你的服务器上，那么调用时，所有的url都要换成http://你服务器的域名/服务路由

## 调用示例
```
import requests

# 测试万年历
url = "http://localhost:5000/WanNianLi"
data = {
    "username":"您的用户名"
    "token": "your_token",
    "year": 2023,
    "month": 5,
    "day": 15
}
response = requests.post(url, json=data)
print(response.json())

# 测试时辰转换
url = "http://localhost:5000/ShiChen?hour=14&token=your_token&username=您的用户名"
response = requests.get(url)
print(response.json())

# 测试梅花易数
url = "http://localhost:5000/MeiHuaZhan"
data = {
    "username":"您的用户名"
    "token": "your_token",
    "first_num": 15,
    "second_num": 7
}
response = requests.post(url, json=data)
print(response.json())
```

### token的获取方式
我们在在代码中显然看见了token验证方法，那么如何获得token呢？
我们可以在main.py同级目录中找到db.txt在以`用户token,用户名`的格式记录用户和用户名
这样就可以简单的实现文件安全验证了
