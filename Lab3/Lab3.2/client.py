import socket
import pickle
import numpy as np
from scipy import ndimage


def send_all(sock, data):
    data = pickle.dumps(data)
    sock.sendall(len(data).to_bytes(4, byteorder='big'))
    sock.sendall(data)


def receive_all(sock):
    length = int.from_bytes(sock.recv(4), byteorder='big')
    data = b''
    while len(data) < length:
        packet = sock.recv(4096)
        if not packet:
            break
        data += packet
    return pickle.loads(data)


def edge_filter(fragment):

    if len(fragment.shape) == 3:
        gray = np.dot(fragment[..., :3], [0.2989, 0.5870, 0.1140])
    else:
        gray = fragment

    sx = ndimage.sobel(gray, axis=0, mode='constant')
    sy = ndimage.sobel(gray, axis=1, mode='constant')

    magnitude = np.hypot(sx, sy)

    if magnitude.max() > 0:
        magnitude = (magnitude / magnitude.max()) * 255

    return magnitude.astype(np.uint8)


def client_main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect(('10.216.39.215', 2040))

    fragment = receive_all(client_socket)
    processed_fragment = edge_filter(fragment)
    send_all(client_socket, processed_fragment)

    client_socket.close()
    print("Fragment przetworzony i wysłany z powrotem do serwera")


if __name__ == "__main__":
    client_main()