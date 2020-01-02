import socket


def make_request(raw_request):
    if isinstance(raw_request, bytes):
        raw_request = raw_request.decode("utf-8")
    # 以下、raw_requestはstr
    print(raw_request)
    header, body = raw_request.split("\r\n\r\n", 1)  # 最初のCRLFで分割
    headers = header.splitlines()  # headerを行で分割
    # headers[0](リクエストライン) 例:GET /hoge HTTP/1.1 を分割
    method, path, proto = headers[0].split(" ", 2)
    request = {
        "headers": headers[1:],
        "body": body,
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "SERVER_PROTOCOL": proto,
    }
    return request


def make_response(status, headers, body):
    status_line = ("HTTP/1.1 " + status).encode("utf-8")
    hl = []
    for k, v in headers:
        h = f"{k}: {v}"
        hl.append(h)
    header = ("\r\n".join(hl)).encode("utf-8")
    if isinstance(body, str):
        body = body.encode("utf-8")
    # bytesのresponseを作って返す
    raw_response = status_line + b"\r\n" + header + b"\r\n\r\n" + body
    print(raw_response)
    return raw_response


def view(request):
    if request["PATH_INFO"] == "/":
        body = """\
        <html>
          <head>
            <link href="/static/style.css" rel="stylesheet">
          </head>
          <body>
            <h1>Hello World!</h1>
            <img src="/static/image.jpg">
          </body>
        </html>
        """
        resp = ("200 OK", [("Content-Type", "text/html")], body)

    elif request["PATH_INFO"] == "/static/style.css":
        headers = [("Content-Type", "text/css")]
        resp = ("200 OK", headers, open("static/style.css", "rb").read())

    elif request["PATH_INFO"] == "/static/image.jpg":
        headers = [("Content-Type", "image/jpg")]
        resp = ("200 OK", headers, open("static/image.jpg", "rb").read())

    else:
        resp = ("404 Not Found", [("Content-Type", "text/plain")], "NO PAGE")
    return resp  # (status str, headers List(tuple), content)


def app(raw_request):
    request = make_request(raw_request)
    status, headers, body = view(request)
    # if isinstance(body, str):  # make_responseの中にあるので重複
    #     body = body.encode('utf-8')
    raw_response = make_response(status, headers, body)
    return raw_response


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
                raw_response = app(raw_request)
                conn.sendall(raw_response)


if __name__ == "__main__":
    main()
