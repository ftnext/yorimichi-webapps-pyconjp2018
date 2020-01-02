from mimetypes import guess_type
import os
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


def index_view(request):
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
    return ("200 OK", [], body)


def file_view(request):
    path = request["PATH_INFO"]
    path = path.lstrip("/")  # remove first /
    if not os.path.isfile(path):
        return notfound_view(request)

    ct, _ = guess_type(path)
    if ct is None:
        ct = "application/octet-stream"
    headers = [("Content-Type", ct)]
    return ("200 OK", headers, open(path, "rb").read())


def notfound_view(request):
    return ("404 NOT FOUND", [], "NO PAGE")


patterns = {
    "/static/": file_view,
    "/": index_view,
}


def dispatch(request):
    path_info = request["PATH_INFO"]
    for path, view in patterns.items():
        if path_info.startswith(path):
            # BUG: path_infoが/hogeのとき、/と一致するのでindex_viewが返る
            return view
    return notfound_view


def app(raw_request):
    request = make_request(raw_request)
    view = dispatch(request)
    status, headers, body = view(request)
    # if isinstance(body, str):  # make_responseの中にあるので重複
    #     body = body.encode('utf-8')
    raw_response = make_response(status, headers, body)
    return raw_response


def wsgiapp(environ, start_response):
    request = environ
    view = dispatch(request)
    status, headers, body = view(request)
    if isinstance(body, str):
        body = body.encode("utf-8")
    start_response(status, headers)
    return [body]


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
