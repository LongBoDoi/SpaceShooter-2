import socket
import struct

##
# Lớp truyền dữ liệu có đóng khung (framing) trên một socket TCP đã kết nối.
#
# Vì sao cần: TCP là dòng byte, không phải "gói tin". recv() có thể trả về một
# phần thông điệp, hoặc gộp nhiều thông điệp. Cách cũ recv(2048) rồi decode giả
# định "một send = một recv" -> hỏng khi dữ liệu > 2048 byte (loạt đạn boss) hoặc
# khi các gói bị gộp/tách. Ở đây mỗi thông điệp được ghi kèm 4 byte độ dài phía
# trước, nên phía nhận luôn đọc đúng trọn một khung.
#
# Ngoài ra bật TCP_NODELAY để tắt thuật toán Nagle - với các gói nhỏ gửi liên
# tục theo kiểu hỏi/đáp, Nagle (kết hợp delayed-ACK) có thể thêm tới ~40ms trễ
# mỗi gói. Tắt nó là cải thiện độ trễ lớn nhất và rẻ nhất cho game thời gian thực.
###
_HEADER = struct.Struct("!I")   # 4 byte, big-endian, unsigned: độ dài phần thân


class FramedConnection:
    def __init__(self, sock):
        self._sock = sock
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            # Bộ đệm rộng: nếu bên kia khựng vài khung (cửa sổ thu nhỏ...) thì gói
            # dồn vào đệm thay vì làm sendall chặn -> game loop bên này vẫn chạy.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
        except OSError:
            pass
        self._buffer = bytearray()      # đệm byte đã nhận nhưng chưa đủ một khung
        self._blocking = None           # trạng thái timeout hiện tại (giảm syscall)

    def _setBlocking(self, blocking):
        if self._blocking is blocking:
            return
        self._sock.settimeout(None if blocking else 0)
        self._blocking = blocking

    ##
    # Gửi trọn một thông điệp (chuỗi) kèm tiền tố độ dài. sendall đảm bảo gửi hết.
    ###
    def sendMessage(self, data):
        payload = data.encode("utf-8")
        try:
            # Gửi ở chế độ chặn để sendall luôn đẩy trọn gói (poll trước đó có thể
            # đã đặt socket sang non-blocking). Gói nhỏ + bên kia rút mỗi khung nên
            # bộ đệm gửi hầu như không đầy -> thực tế không chặn game loop.
            self._setBlocking(True)
            self._sock.sendall(_HEADER.pack(len(payload)) + payload)
            return True
        except OSError:
            return False

    ##
    # Đọc CHẶN cho tới khi nhận trọn một khung. Trả "" nếu kết nối đứt.
    ###
    def receiveMessage(self):
        self._setBlocking(True)
        header = self._readExact(4)
        if header is None:
            return ""
        (length,) = _HEADER.unpack(header)
        body = self._readExact(length)
        if body is None:
            return ""
        return body.decode("utf-8")

    ##
    # Đọc KHÔNG CHẶN: nạp dữ liệu sẵn có rồi trả về một khung hoàn chỉnh nếu đã đủ,
    # ngược lại trả "" (dữ liệu dở dang được giữ lại trong đệm cho lần sau).
    ###
    def poll(self):
        self._setBlocking(False)
        while True:
            try:
                chunk = self._sock.recv(4096)
            except (BlockingIOError, socket.timeout):
                break
            except OSError:
                break
            if not chunk:
                break
            self._buffer.extend(chunk)
        frame = self._extractFrame()
        return frame if frame is not None else ""

    ##
    # Lấy đúng n byte (ưu tiên từ đệm, thiếu thì recv chặn thêm). None nếu đứt.
    ###
    def _readExact(self, n):
        while len(self._buffer) < n:
            try:
                chunk = self._sock.recv(4096)
            except OSError:
                return None
            if not chunk:
                return None
            self._buffer.extend(chunk)
        result = bytes(self._buffer[:n])
        del self._buffer[:n]
        return result

    ##
    # Thử tách một khung hoàn chỉnh khỏi đệm (không đọc thêm từ socket).
    ###
    def _extractFrame(self):
        if len(self._buffer) < 4:
            return None
        (length,) = _HEADER.unpack(bytes(self._buffer[:4]))
        if len(self._buffer) < 4 + length:
            return None
        body = bytes(self._buffer[4:4 + length])
        del self._buffer[:4 + length]
        return body.decode("utf-8")

    ##
    # Vứt sạch dữ liệu tồn đọng (đệm nội bộ + những gì đang chờ trong socket).
    # Dùng khi bắt đầu ván mới để bỏ các gói dở của ván trước trên cùng kết nối.
    ###
    def flush(self):
        self._buffer.clear()
        self._setBlocking(False)
        while True:
            try:
                if not self._sock.recv(65536):
                    break            # kết nối đóng
            except (BlockingIOError, socket.timeout):
                break                # hết dữ liệu đang chờ
            except OSError:
                break

    def close(self):
        try:
            self._sock.close()
        except OSError:
            pass
