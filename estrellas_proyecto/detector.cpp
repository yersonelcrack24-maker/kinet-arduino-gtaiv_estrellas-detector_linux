#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <opencv2/opencv.hpp>

int abrir_puerto(const char* puerto) {
    int fd = open(puerto, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd == -1) return -1;
    
    struct termios opciones;
    tcgetattr(fd, &opciones);
    cfsetispeed(&opciones, B115200);
    cfsetospeed(&opciones, B115200);
    opciones.c_cflag |= (CLOCAL | CREAD);
    opciones.c_cflag &= ~PARENB;
    opciones.c_cflag &= ~CSTOPB;
    opciones.c_cflag &= ~CSIZE;
    opciones.c_cflag |= CS8;
    opciones.c_cflag &= ~CRTSCTS;
    opciones.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    opciones.c_oflag &= ~OPOST;
    tcsetattr(fd, TCSANOW, &opciones);
    return fd;
}

inline bool identificador_de_muestras(const cv::Mat& gray, const cv::Mat& ejemplo, double prob, cv::Mat& res) {
    if (ejemplo.empty()) return false;
    cv::matchTemplate(gray, ejemplo, res, cv::TM_CCOEFF_NORMED);
    return cv::countNonZero(res >= prob) > 0;
}

int main() {
    cv::Mat uno = cv::imread("1.png", 0);
    cv::Mat dos = cv::imread("2.png", 0);
    if (uno.empty() || dos.empty()) return -1;

    cv::VideoCapture pantalla(0);
    if (!pantalla.isOpened()) return -1;

    int serial_fd = abrir_puerto("/dev/ttyUSB0");

    cv::Mat frame, gray, res;
    // Pre-reservar para no crear memoria en cada loop

    while (true) {
        pantalla >> frame;
        if (frame.empty()) {
            usleep(10000);
            continue;
        }

        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

        bool policia = identificador_de_muestras(gray, uno, 0.64, res) || 
                       identificador_de_muestras(gray, dos, 0.7, res);

        if (serial_fd != -1) {
            if (policia) {
                for (int i = 0; i < 15; i++) {
                    write(serial_fd, "l", 1);
                    write(serial_fd, "p", 1);
                    usleep(80000);
                    write(serial_fd, "k", 1);
                    write(serial_fd, "n", 1);
                    usleep(80000);
                }
            } else {
                write(serial_fd, "k", 1);
                write(serial_fd, "p", 1);
                usleep(50000);
            }
        }
    }

    if (serial_fd != -1) close(serial_fd);
    return 0;
}
