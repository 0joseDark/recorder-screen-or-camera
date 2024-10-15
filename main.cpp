#include <QApplication>
#include <QPushButton>
#include <QLabel>
#include <QRadioButton>
#include <QFileDialog>
#include <QMessageBox>
#include <QVBoxLayout>
#include <QListWidget>
#include <QThread>
#include <QTimer>
#include <opencv2/opencv.hpp>
#include <iostream>

class ScreenRecorder : public QWidget {
    Q_OBJECT

public:
    ScreenRecorder(QWidget *parent = nullptr);
    ~ScreenRecorder();

private slots:
    void refreshWindows();
    void selectFile();
    void startRecording();
    void stopRecording();

private:
    QRadioButton *cameraRadioButton;
    QRadioButton *windowRadioButton;
    QListWidget *windowListWidget;
    QPushButton *selectFileButton;
    QPushButton *recordButton;
    QPushButton *stopButton;
    QPushButton *exitButton;
    QString filePath;
    bool recording;
    std::vector<std::string> windows;
    cv::VideoCapture cap;
    cv::VideoWriter writer;
    QTimer *recordingTimer;

    void recordCamera();
    void recordWindow();
};

ScreenRecorder::ScreenRecorder(QWidget *parent) : QWidget(parent), recording(false) {
    QVBoxLayout *layout = new QVBoxLayout(this);

    QLabel *label = new QLabel("Escolha a fonte de gravação:", this);
    layout->addWidget(label);

    cameraRadioButton = new QRadioButton("Câmera USB", this);
    windowRadioButton = new QRadioButton("Janela", this);
    layout->addWidget(cameraRadioButton);
    layout->addWidget(windowRadioButton);

    windowListWidget = new QListWidget(this);
    layout->addWidget(windowListWidget);

    QPushButton *refreshButton = new QPushButton("Atualizar Janelas", this);
    connect(refreshButton, &QPushButton::clicked, this, &ScreenRecorder::refreshWindows);
    layout->addWidget(refreshButton);

    selectFileButton = new QPushButton("Escolher Local e Nome do Arquivo", this);
    connect(selectFileButton, &QPushButton::clicked, this, &ScreenRecorder::selectFile);
    layout->addWidget(selectFileButton);

    recordButton = new QPushButton("Gravar", this);
    connect(recordButton, &QPushButton::clicked, this, &ScreenRecorder::startRecording);
    layout->addWidget(recordButton);

    stopButton = new QPushButton("Parar Gravação", this);
    stopButton->setEnabled(false);
    connect(stopButton, &QPushButton::clicked, this, &ScreenRecorder::stopRecording);
    layout->addWidget(stopButton);

    exitButton = new QPushButton("Sair", this);
    connect(exitButton, &QPushButton::clicked, this, &QApplication::quit);
    layout->addWidget(exitButton);

    setLayout(layout);
}

ScreenRecorder::~ScreenRecorder() {
    if (recording) {
        stopRecording();
    }
}

void ScreenRecorder::refreshWindows() {
    // Função simulada para listar janelas (pode integrar com o Qt para listar janelas do SO)
    windowListWidget->clear();
    windows.push_back("Janela 1");
    windows.push_back("Janela 2");

    for (const std::string &window : windows) {
        windowListWidget->addItem(QString::fromStdString(window));
    }
}

void ScreenRecorder::selectFile() {
    filePath = QFileDialog::getSaveFileName(this, "Escolher Local e Nome do Arquivo", "", "Video Files (*.avi)");
    if (!filePath.isEmpty()) {
        QMessageBox::information(this, "Info", "Arquivo selecionado: " + filePath);
    }
}

void ScreenRecorder::startRecording() {
    if (cameraRadioButton->isChecked()) {
        recordCamera();
    } else if (windowRadioButton->isChecked() && !windowListWidget->selectedItems().isEmpty()) {
        recordWindow();
    } else {
        QMessageBox::warning(this, "Aviso", "Por favor, selecione uma opção de gravação.");
        return;
    }

    recordButton->setEnabled(false);
    stopButton->setEnabled(true);
    exitButton->setEnabled(false);
}

void ScreenRecorder::stopRecording() {
    recording = false;
    recordButton->setEnabled(true);
    stopButton->setEnabled(false);
    exitButton->setEnabled(true);

    if (cap.isOpened()) {
        cap.release();
    }

    if (writer.isOpened()) {
        writer.release();
    }
}

void ScreenRecorder::recordCamera() {
    cap.open(0);
    if (!cap.isOpened()) {
        QMessageBox::critical(this, "Erro", "Não foi possível acessar a câmera.");
        return;
    }

    int width = static_cast<int>(cap.get(cv::CAP_PROP_FRAME_WIDTH));
    int height = static_cast<int>(cap.get(cv::CAP_PROP_FRAME_HEIGHT));
    writer.open(filePath.toStdString(), cv::VideoWriter::fourcc('X', 'V', 'I', 'D'), 20, cv::Size(width, height));

    if (!writer.isOpened()) {
        QMessageBox::critical(this, "Erro", "Não foi possível abrir o arquivo de saída.");
        return;
    }

    recording = true;
    recordingTimer = new QTimer(this);
    connect(recordingTimer, &QTimer::timeout, this, &ScreenRecorder::recordCamera);
    recordingTimer->start(50);

    while (recording) {
        cv::Mat frame;
        cap >> frame;
        if (frame.empty()) break;
        writer.write(frame);
    }

    stopRecording();
}

void ScreenRecorder::recordWindow() {
    // Implementar gravação de janelas usando OpenCV + captura de tela (pyautogui pode ser substituído por Qt ou outros métodos)
    QMessageBox::information(this, "Info", "Gravação de janela ainda não implementada.");
}

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    ScreenRecorder recorder;
    recorder.show();
    return app.exec();
}

#include "main.moc"
