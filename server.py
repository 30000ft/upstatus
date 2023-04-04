import socket
import smtplib
from email.message import EmailMessage
from threading import Thread
import time
import os
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

# 读取环境变量
server_port = int(os.getenv("SERVER_PORT"))
timeout = int(os.getenv("TIMEOUT"))
email_sender = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
email_recipient = os.getenv("EMAIL_RECIPIENT")

clients = {}  # 存储客户端的IP地址和状态

def send_email_notification(subject, content):
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = email_sender
    msg["To"] = email_recipient

    server = smtplib.SMTP_SSL("smtp.example.com", 465)
    server.login(email_sender, email_password)
    server.send_message(msg)
    server.quit()

def handle_client(conn, addr):
    global clients
    conn.settimeout(timeout)
    try:
        ip = addr[0]
        clients[ip] = False

        while True:
            data = conn.recv(1024)
            if not data:
                break

            if data.decode() == "heartbeat":
                print(f"来自 {ip} 的心跳消息。")
                if clients[ip]:
                    clients[ip] = False
                    send_email_notification(f"{ip}网络恢复通知", f"{ip}内网与互联网重新连接了。")
                else:
                    clients[ip] = True
                conn.send("ok".encode())
            else:
                print(f"来自 {ip} 的无效心跳消息。")

    except socket.timeout:
        if not clients[ip]:
            clients[ip] = True
            send_email_notification(f"{ip}网络中断通知", f"{ip}内网与互联网断开连接了。")
    finally:
        conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", server_port))
    s.listen()
    print(f"服务器已启动，正在监听端口 {server_port}。")

    while True:
        conn, addr = s.accept()

        # 在新线程中处理客户端连接
        Thread(target=handle_client, args=(conn, addr)).start()