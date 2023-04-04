import socket
import time
import os
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

# 读取环境变量
server_host = os.getenv("SERVER_HOST")
server_port = int(os.getenv("SERVER_PORT"))
heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL"))
client_name = os.getenv("CLIENT_NAME")

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_host, server_port))
            while True:
                s.send("heartbeat".encode())
                data = s.recv(1024)
                if not data:
                    break
                print(f"{client_name}已发送心跳。")
                print(f"来自服务器的响应：{data.decode()}"
                time.sleep(heartbeat_interval)
    except ConnectionRefusedError:
        print(f"连接到服务器 {server_host}:{server_port} 失败，请检查服务端是否已启动，或者未连接网络。")
        break
    except KeyboardInterrupt:
        print(f"{client_name}已停止心跳发送。")
        break
