Para instalar os módulos necessários no Ubuntu para o seu script Python, siga os passos abaixo:

1. **Instalar o `pip`:** Se você ainda não tiver o `pip`, pode instalá-lo com:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip
   ```

2. **Instalar o `tkinter`:** No Ubuntu, o `tkinter` é instalado separadamente, pois ele não vem incluído por padrão com Python.
   ```bash
   sudo apt-get install python3-tk
   ```

3. **Instalar outros módulos com `pip`:** Depois de ter o `pip`, você pode instalar os módulos adicionais usados no script. Execute o comando abaixo para instalar todos de uma vez:
   ```bash
   pip3 install pygetwindow pyautogui opencv-python numpy
   ```

   - **`pygetwindow`**: Para manipular janelas abertas.
   - **`pyautogui`**: Para capturar capturas de tela.
   - **`opencv-python`**: Para gravação e manipulação de vídeo.
   - **`numpy`**: Para operações com arrays e manipulação de imagem.

### Verificando a Instalação
Para garantir que tudo foi instalado corretamente, você pode rodar o seguinte comando:
```bash
python3 -m pip show tkinter pygetwindow pyautogui opencv-python numpy
```

Se os módulos aparecerem na lista, eles foram instalados corretamente e devem estar prontos para uso no seu script.