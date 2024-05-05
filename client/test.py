import socket

tcp_cilent = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcp_cilent.connect(("localhost",8080))

def get_png():
    request =   b'GET /static/icons/love-message.png HTTP/1.1\r\n' \
                b'Host: localhost:8080\r\n'\
                b'Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8\r\n'\
                b'Accept-Encoding: gzip, deflate, br, zstd\r\n'\
                b'Accept-Language: en-US;q=0.9\r\n'\
                b'Connection: keep-alive\r\n'\
                b'\r\n'
                
    tcp_cilent.sendall(request)

def main():
    for i in range(50):
        get_png()

if __name__ == '__main__':
    main()