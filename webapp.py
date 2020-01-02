import random
import socket


def view(raw_request):
    print(raw_request)  # raw_requestはstrで受け取る
    resp_list = [
        "HTTP/1.1 404 Not Found\r\n\r\nNo Page\n",
        "HTTP/1.1 402 Payment Required\r\n\r\nOkane Choudai\n",
        "HTTP/1.1 501 Not Implemented\r\n\r\nMada Dayo\n",
    ]
    resp = random.choice(resp_list)
    return resp


def main():
    # IPv4, TCP通信のサーバソケット
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 8000))
        s.listen()  # サーバが接続を待ち受ける
        while True:
            conn, addr = s.accept()  # 接続受け付け。connはクライアントソケット
            with conn:
                raw_request = b""
                while True:
                    chunk = conn.recv(4096)
                    # idea: 4096byteちょうどで固まる問題、RuntimeErrorを挙げる？
                    # if chunk == b'':
                    #     raise RuntimeError("socket connection broken")
                    # ref: https://docs.python.org/ja/3/howto/sockets.html
                    raw_request += chunk
                    if len(chunk) < 4096:
                        break
                raw_response = view(raw_request.decode("utf-8"))
                conn.sendall(raw_response.encode("utf-8"))


if __name__ == "__main__":
    main()