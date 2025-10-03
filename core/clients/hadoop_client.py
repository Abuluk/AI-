# 在本地计算机的Web后端项目中创建 hadoop_client.py
import requests

class HadoopWebClient:
    def __init__(self, vm_ip="your-hadoop01-ip", api_port=8080):
        self.base_url = f"http://{vm_ip}:{api_port}"
    
    def test_connection(self):
        """测试推荐API连接"""
        # 尝试多个可能的健康检查端点
        health_endpoints = [
            "/",
            "/health",
            "/api/v1/",
            "/api/v1/ai_strategy/",
            "/docs",
            "/openapi.json"
        ]
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                print(f"测试端点 {endpoint}: 状态码 {response.status_code}")
                if response.status_code == 200:
                    print(f"成功连接到推荐API: {self.base_url}{endpoint}")
                    return True
            except requests.exceptions.ConnectTimeout:
                print(f"连接超时: 无法连接到 {self.base_url}{endpoint}")
                continue
            except requests.exceptions.ConnectionError:
                print(f"连接错误: 无法连接到 {self.base_url}{endpoint}")
                continue
            except Exception as e:
                print(f"请求失败 {endpoint}: {e}")
                continue
        
        print("所有健康检查端点都失败")
        return False

    def get_recommendations(self, user_id):
        """通过HTTP API获取推荐结果"""
        try:
            # 使用正确的API路径：/recommendations/{user_id}
            response = requests.get(f"{self.base_url}/recommendations/{user_id}", timeout=5)
            print(f"请求URL: {self.base_url}/recommendations/{user_id}")
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"解析后的JSON: {result}")
                    return result
                except ValueError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"原始响应: {response.text}")
                    return {"error": "JSON解析失败", "raw_response": response.text}
            elif response.status_code == 422:
                print(f"数据验证错误 (422): 可能是user_id参数格式问题")
                print(f"错误详情: {response.text}")
                return {"error": "数据验证错误", "status_code": 422, "detail": response.text}
            else:
                print(f"HTTP错误: {response.status_code}")
                return {"error": f"HTTP错误: {response.status_code}", "detail": response.text}
        except requests.exceptions.ConnectTimeout:
            print(f"连接超时: 无法连接到 {self.base_url}")
            return {"error": "连接超时"}
        except requests.exceptions.ConnectionError:
            print(f"连接错误: 无法连接到 {self.base_url}")
            return {"error": "连接错误"}
        except Exception as e:
            print(f"请求失败: {e}")
            return {"error": f"请求失败: {str(e)}"}

    def test_different_endpoints(self, user_id):
        """测试不同的API端点以找到正确的路径"""
        endpoints_to_test = [
            f"/api/v1/ai_strategy/recommendations?user_id={user_id}",
            f"/api/v1/ai_strategy/recommendations?user_id={user_id}&limit=10",
            f"/api/v1/recommendations/{user_id}",
            f"/recommendations/{user_id}",
            f"/api/v1/ai_strategy/recommendations",
        ]
        
        print(f"\n=== 测试不同API端点 ===")
        for endpoint in endpoints_to_test:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"\n测试端点: {url}")
                response = requests.get(url, timeout=5)
                print(f"状态码: {response.status_code}")
                if response.status_code == 200:
                    print(f"成功! 响应: {response.text[:200]}...")
                else:
                    print(f"失败: {response.text[:100]}...")
            except Exception as e:
                print(f"异常: {e}")

# 使用示例
if __name__ == "__main__":
    # 创建Hadoop客户端实例
    hadoop_client = HadoopWebClient("192.168.174.128", 8080)  # 虚拟机IP - 使用YARN ResourceManager端口
    
    # 测试连接
    print("测试Hadoop连接...")
    if hadoop_client.test_connection():
        print("\n测试推荐API...")
        
        # 首先测试不同的API端点
        print("\n=== 第一步：测试API端点 ===")
        hadoop_client.test_different_endpoints("1")
        
        print("\n=== 第二步：测试推荐功能 ===")
        # 测试不同的用户ID
        test_user_ids = ["1", "123", "test_user"]
        
        for user_id in test_user_ids:
            print(f"\n--- 测试用户ID: {user_id} ---")
            result = hadoop_client.get_recommendations(user_id)
            print(f"推荐结果: {result}")
            
            # 如果找到有效用户，就停止测试
            if result and "error" not in result:
                print(f"找到有效用户 {user_id} 的推荐数据！")
                break
    else:
        print("无法连接到Hadoop服务器")