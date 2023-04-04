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
heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL"))
heartbeat_timeout = int(os.getenv("HEARTBEAT_TIMEOUT"))
email_sender = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
email_recipient = os.getenv("EMAIL_RECIPIENT")
smtpemail_host = os.getenv("SMTPEMAIL_HOST")

clients_connected = {}  # 存储客户端的IP地址和状态

def send_email_notification(subject, content):
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = email_sender
    msg["To"] = email_recipient

    server = smtplib.SMTP_SSL(smtpemail_host, 465)
    server.login(email_sender, email_password)
    server.send_message(msg)
    print(f"已向 {email_recipient} 发送邮件。")
    server.quit()

def handle_client(conn, addr):
    global clients_connected
    conn.settimeout(heartbeat_timeout)
    try:
        ip = addr[0]
        clients_connected[ip] = False

        while True:
            data = conn.recv(1024)
            if not data:
                break

            if data.decode() == "heartbeat":
                if not clients_connected[ip]:
                    print(f"来自 {ip} 的心跳消息。")
                    clients_connected[ip] = True
                    #add timestamp
                    send_email_notification(f"{ip}网络恢复通知", f"{ip}内网与互联网重新连接了。")
                else:
                    print(f"来自 {ip} 的重复心跳消息。",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                conn.send("ok".encode())
            else:
                print(f"来自 {ip} 的无效心跳消息。")

    except socket.timeout:
        if clients_connected[ip]:
            print(f"来自 {ip} 的超时消息。")
            clients_connected[ip] = False
            send_email_notification(f"{ip}网络中断通知", f"{ip}内网与互联网断开连接了。")
            print(f"已向 {email_recipient} 发送邮件。except")
        else:
            print(f"来自 {ip} 的重复超时消息。", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    finally:
        if clients_connected[ip]:
            print(f"来自 {ip} 的超时消息，连接已断开")
            clients_connected[ip] = False
            send_email_notification(f"{ip}网络中断通知", f"{ip}内网与互联网断开连接了。")
            print(f"已向 {email_recipient} 发送邮件。finally")
            conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", server_port))
    s.listen()
    print(f"服务器已启动，正在监听端口 {server_port}。")

    while True:
        conn, addr = s.accept()

        # 在新线程中处理客户端连接
        Thread(target=handle_client, args=(conn, addr)).start()
