import cv2
import tensorflow as tf

# Carregar o modelo TensorFlow
model = tf.keras.models.load_model("model.h5")

# Iniciar a captura da webcam
cap = cv2.VideoCapture(0)

# Loop infinito para capturar frames da webcam
while True:
    # Ler um frame da webcam
    ret, frame = cap.read()

    # Pré-processamento do frame
    # Converta o frame para RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Redimensione o frame para o tamanho de entrada do modelo
    frame = cv2.resize(frame, (224, 224))
    # Normalize os valores dos pixels
    frame = frame / 255.0

    # Fazer a predição com o modelo TensorFlow
    prediction = model.predict(frame)

    # Adicionar a predição ao frame
    cv2.putText(frame, str(prediction), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Mostrar o frame na tela
    cv2.imshow("Camera", frame)

    # Aperte 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar a captura da webcam
cap.release()

# Destruir todas as janelas
cv2.destroyAllWindows()
