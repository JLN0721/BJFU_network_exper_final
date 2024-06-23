"""
在命令行方式下指定服务器的IP地址和端口。
创建UDP套接字并绑定到本地端口。
构造请求报文，包括序列号和版本号，并发送给服务器。
设置超时时间为100ms，等待服务器的响应。
如果在超时时间内收到响应，则计算往返时间（RTT），打印出相关信息。
如果超时，则重新发送请求报文，最多尝试两次，每次重传后等待100ms。
完成12次请求后，打印汇总信息，包括接收到的UDP数据包数量、丢包率、最大RTT、最小RTT、平均RTT、RTT的标准差以及服务器的整体响应时间。
"""
import socket
import time
import struct
import random
import string
import sys

TIMEOUT = 0.1
RETRIES = 2
NUM_PACKETS = 12
VERSION = 2

first_response_time = None
last_response_time = None


def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def validate_arguments(server_ip, server_port):
    if not is_valid_ip(server_ip):
        print(f"无效的 IP 地址: {server_ip}")
        sys.exit(1)
    if not (0 <= server_port <= 65535):
        print(f"无效的端口号: {server_port}. 端口号必须在0到65535之间")
        sys.exit(1)


def initialize_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
    return client_socket


def create_packet(seq_num):
    random_data = ''.join(random.choices(string.ascii_lowercase + string.digits, k=200)).encode('utf-8')
    return struct.pack('!H B 200s', seq_num, VERSION, random_data)


def send_packet(client_socket, packet, server_ip, server_port):
    global first_response_time, last_response_time

    if first_response_time is None:
        first_response_time = time.time()

    start_time = time.time()
    client_socket.sendto(packet, (server_ip, server_port))

    try:
        response, _ = client_socket.recvfrom(4096)
        end_time = time.time()
        rtt = (end_time - start_time) * 1000

        seq_no, ver, sys_time = struct.unpack('!H B 200s', response)
        sys_time = sys_time.decode('utf-8').rstrip('\x00')

        print(f"序号: {seq_no}, 服务器 IP:端口: {server_ip}:{server_port}, RTT: {rtt:.2f}ms, 服务器时间: {sys_time}")

        last_response_time = max(last_response_time, time.time()) if last_response_time else time.time()
        return rtt, True
    except (socket.timeout, struct.error, Exception) as e:
        if isinstance(e, socket.timeout):
            print(f"序号: {struct.unpack('!H', packet[:2])[0]}, 请求超时")
        elif isinstance(e, struct.error):
            print(f"解包响应报文时出错: {e}")
        else:
            print(f"接收响应报文时出错: {e}")
        return None, False


def calculate_statistics(rtts):
    max_rtt = max(rtts)
    min_rtt = min(rtts)
    avg_rtt = sum(rtts) / len(rtts)
    std_dev_rtt = (sum((x - avg_rtt) ** 2 for x in rtts) / len(rtts)) ** 0.5

    print(f"最大RTT: {max_rtt:.2f}ms")
    print(f"最小RTT: {min_rtt:.2f}ms")
    print(f"平均RTT: {avg_rtt:.2f}ms")
    print(f"RTT标准差: {std_dev_rtt:.2f}ms")


def main():
    if len(sys.argv) != 3:
        print("输入的参数个数不是3个，请重新输入。")
        sys.exit(1)

    server_ip = sys.argv[1]
    try:
        server_port = int(sys.argv[2])
    except ValueError:
        print("端口号必须是整数。")
        sys.exit(1)

    validate_arguments(server_ip, server_port)

    client_socket = initialize_socket()

    received_packets = 0
    rtts = []

    global first_response_time, last_response_time
    try:
        for i in range(1, NUM_PACKETS + 1):
            packet = create_packet(i)
            for attempt in range(RETRIES + 1):
                rtt, success = send_packet(client_socket, packet, server_ip, server_port)
                if success:
                    received_packets += 1
                    rtts.append(rtt)
                    break
                elif attempt == RETRIES:
                    print(f"序号: {i}, 请求失败，共重传 {RETRIES} 次")
    finally:
        client_socket.close()

    if rtts:
        print(f"接收到的UDP报文数量: {received_packets}")
        print(f"丢包率: {(1 - received_packets / NUM_PACKETS) * 100:.2f}%")
        calculate_statistics(rtts)

        response_time_difference = last_response_time - first_response_time
        print(f"服务器整体响应时间之差: {response_time_difference * 1000:.2f}ms")
    else:
        print("未接收到任何报文。")


if __name__ == '__main__':
    main()



# import socket
# import time
# import struct
# import random
# import string
# import sys
#
# # 配置参数
# TIMEOUT = 0.1  # 100ms 超时
# RETRIES = 2  # 重传次数
# NUM_PACKETS = 12  # 发送报文数量
# VERSION = 2  # 版本号
#
#
# def is_valid_ip(ip):
#     """验证IP地址格式"""
#     try:
#         socket.inet_aton(ip)
#         return True
#     except socket.error:
#         return False
#
#
# def validate_arguments(server_ip, server_port):
#     """验证命令行参数"""
#     if not is_valid_ip(server_ip):
#         print(f"无效的 IP 地址: {server_ip}")
#         sys.exit(1)
#     if not (0 <= server_port <= 65535):
#         print(f"无效的端口号: {server_port}. 端口号必须在0到65535之间")
#         sys.exit(1)
#
#
# def initialize_socket():
#     """初始化socket"""
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     client_socket.settimeout(TIMEOUT)
#     return client_socket
#
#
# def create_packet(seq_num):
#     """创建数据包"""
#     random_data = ''.join(random.choices(string.ascii_lowercase + string.digits, k=200)).encode('utf-8')
#     return struct.pack('!H B 200s', seq_num, VERSION, random_data)
#
#
# def send_packet(client_socket, packet, server_ip, server_port, first_response_time, last_response_time):
#     """发送报文并接收响应"""
#     if first_response_time is None:
#         first_response_time = time.time()
#     start_time = time.time()
#     client_socket.sendto(packet, (server_ip, server_port))
#
#     try:
#         response, _ = client_socket.recvfrom(4096)
#         end_time = time.time()
#         rtt = (end_time - start_time) * 1000
#         seq_no, ver, sys_time = struct.unpack('!H B 200s', response)
#         sys_time = sys_time.decode('utf-8').rstrip('\x00')
#         print(f"序号: {seq_no}, 服务器 IP:端口: {server_ip}:{server_port}, RTT: {rtt:.2f}ms, 服务器时间: {sys_time}")
#
#         last_response_time = max(last_response_time, time.time())
#         return rtt, True, first_response_time, last_response_time
#     except socket.timeout:
#         print(f"序号: {struct.unpack('!H', packet[:2])[0]}, 请求超时")
#         return None, False, first_response_time, last_response_time
#     except struct.error as e:
#         print(f"解包响应报文时出错: {e}")
#         return None, False, first_response_time, last_response_time
#     except Exception as e:
#         print(f"接收响应报文时出错: {e}")
#         return None, False, first_response_time, last_response_time
#
#
# def calculate_statistics(rtts):
#     """计算并打印RTT统计信息"""
#     max_rtt = max(rtts)
#     min_rtt = min(rtts)
#     avg_rtt = sum(rtts) / len(rtts)
#     std_dev_rtt = (sum((x - avg_rtt) ** 2 for x in rtts) / len(rtts)) ** 0.5
#     print(f"最大RTT: {max_rtt:.2f}ms")
#     print(f"最小RTT: {min_rtt:.2f}ms")
#     print(f"平均RTT: {avg_rtt:.2f}ms")
#     print(f"RTT标准差: {std_dev_rtt:.2f}ms")
#
#
# def main():
#     if len(sys.argv) != 3:
#         print("输入的参数个数不是3个，请重新输入。")
#         sys.exit(1)
#
#     server_ip = sys.argv[1]
#     try:
#         server_port = int(sys.argv[2])
#     except ValueError:
#         print("端口号必须是整数。")
#         sys.exit(1)
#
#     validate_arguments(server_ip, server_port)
#     client_socket = initialize_socket()
#
#     received_packets = 0
#     rtts = []
#
#     first_response_time = None
#     last_response_time = None
#
#     try:
#         for i in range(1, NUM_PACKETS + 1):
#             packet = create_packet(i)
#             for attempt in range(RETRIES + 1):
#                 rtt, success, first_response_time, last_response_time = send_packet(
#                     client_socket, packet, server_ip, server_port, first_response_time, last_response_time
#                 )
#                 if success:
#                     received_packets += 1
#                     rtts.append(rtt)
#                     break
#                 elif attempt == RETRIES:
#                     print(f"序号: {i}, 请求失败，共重传 {RETRIES} 次")
#     finally:
#         client_socket.close()
#
#     if rtts:
#         print(f"接收到的UDP报文数量: {received_packets}")
#         print(f"丢包率: {(1 - received_packets / NUM_PACKETS) * 100:.2f}%")
#         calculate_statistics(rtts)
#         response_time_difference = last_response_time - first_response_time
#         print(f"服务器整体响应时间之差: {response_time_difference * 1000:.2f}ms")
#     else:
#         print("未接收到任何报文。")
#
#
# if __name__ == '__main__':
#     main()
