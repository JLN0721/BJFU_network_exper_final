"""
创建UDP套接字并绑定到指定的IP地址和端口。
接收来自客户端的请求报文。
解析请求报文，提取序列号（sequence number）和版本号（version）。
如果收到请求，则随机决定是否响应，模拟丢包场景。
如果响应，则构造响应报文，包括序列号和版本号，并附加服务器系统时间等其他内容。
发送响应报文给客户端。
"""
import socket
import random
import struct
import time

# 配置参数
SERVER_IP = '0.0.0.0'
SERVER_PORT = 34109
LOSS_RATE = 0.3


def initialize_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"服务器监听于 {SERVER_IP}:{SERVER_PORT}")
    return server_socket


def unpack_request(request):
    try:
        seq_no, ver, message = struct.unpack('!H B 200s', request)
        return seq_no, ver, message
    except struct.error as e:
        print(f"解包请求报文时出错: {e}")
        return None, None, None


def pack_response(seq_no, ver, server_time):
    try:
        return struct.pack('!H B 200s', seq_no, ver, server_time)
    except struct.error as e:
        print(f"打包响应报文时出错: {e}")
        return None


def handle_request(request, client_address, server_socket):
    seq_no, ver, message = unpack_request(request)
    if seq_no is None:
        return

    if random.random() < LOSS_RATE:
        print(f"序号: {seq_no}, 报文丢失")
        return

    server_time = time.strftime('%H-%M-%S').encode('utf-8')
    response = pack_response(seq_no, ver, server_time)
    if response:
        try:
            server_socket.sendto(response, client_address)
            print(f"序号: {seq_no}, 响应已发送")
            print("报文信息：", message)
        except Exception as e:
            print(f"发送响应报文时出错: {e}")


def main():
    server_socket = initialize_socket()
    try:
        while True:
            try:
                request, client_address = server_socket.recvfrom(4096)
                handle_request(request, client_address, server_socket)
            except Exception as e:
                print(f"接收客户端请求时出错: {e}")
    finally:
        server_socket.close()
        print("服务器已关闭")


if __name__ == '__main__':
    main()

#
# import socket
# import random
# import struct
# import time
#
# SERVER_IP = '0.0.0.0'  # 监听所有接口
# SERVER_PORT = 33909  # 服务器端口
# LOSS_RATE = 0.3  # 丢包率
#
# def initialize_socket(ip, port):
#     """初始化并绑定一个UDP套接字。"""
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建UDP套接字
#     server_socket.bind((ip, port))  # 绑定套接字到指定地址和端口
#     print(f"服务器监听于 {ip}:{port}")  # 打印服务器监听信息
#     return server_socket  # 返回套接字对象
#
# def unpack_request(request):
#     """解包客户端的请求。"""
#     try:
#         seq_no, ver, message = struct.unpack('!H B 200s', request)  # 解包请求报文
#         return seq_no, ver, message.strip()  # 返回解包后的数据
#     except struct.error as e:
#         print(f"解包请求报文时出错: {e}")  # 打印解包错误信息
#         return None, None, None  # 返回空值表示解包失败
#
# def simulate_packet_loss(loss_rate):
#     """根据给定的丢包率模拟丢包。"""
#     return random.random() < loss_rate  # 随机模拟丢包
#
# def pack_response(seq_no, ver, server_time):
#     """打包服务器的响应。"""
#     try:
#         response = struct.pack('!H B 200s', seq_no, ver, server_time)  # 打包响应报文
#         return response  # 返回打包好的响应报文
#     except struct.error as e:
#         print(f"打包响应报文时出错: {e}")  # 打印打包错误信息
#         return None  # 返回空值表示打包失败
#
# def handle_request(request, client_address, server_socket):
#     """处理客户端的请求并发送响应。"""
#     seq_no, ver, message = unpack_request(request)  # 解包请求报文
#     if seq_no is None:
#         return  # 如果解包失败，直接返回
#
#     if simulate_packet_loss(LOSS_RATE):
#         print(f"序号: {seq_no}, 报文丢失")  # 打印丢包信息
#         return  # 丢包，直接返回
#
#     server_time = time.strftime('%H-%M-%S').encode('utf-8')  # 获取当前系统时间并编码为字节串
#     response = pack_response(seq_no, ver, server_time)  # 打包响应报文
#     if response:
#         try:
#             server_socket.sendto(response, client_address)  # 发送响应报文
#             print(f"序号: {seq_no}, 响应已发送")  # 打印响应发送信息
#             print(f"报文信息: {message}")  # 打印接收到的报文信息
#         except Exception as e:
#             print(f"发送响应报文时出错: {e}")  # 打印发送错误信息
#
# def main():
#     """主函数，用于初始化服务器并处理请求。"""
#     server_socket = initialize_socket(SERVER_IP, SERVER_PORT)  # 初始化套接字
#     try:
#         while True:
#             try:
#                 request, client_address = server_socket.recvfrom(4096)  # 接收客户端请求
#                 handle_request(request, client_address, server_socket)  # 处理客户端请求
#             except Exception as e:
#                 print(f"接收客户端请求时出错: {e}")  # 打印接收错误信息
#     finally:
#         server_socket.close()  # 关闭套接字
#         print("服务器已关闭")  # 打印服务器关闭信息
#
# if __name__ == '__main__':
#     main()
