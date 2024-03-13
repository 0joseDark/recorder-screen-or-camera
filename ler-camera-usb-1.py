# ler-camera-usb-6.py
import cv2

# Iniciar a captura da webcam
cap = cv2.VideoCapture(0)

while True:
    # Ler um frame da webcam
    ret, frame = cap.read()

    # Mostrar o frame na tela
    cv2.imshow("Camera", frame)

    # Aperte 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
