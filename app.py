import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QListWidget, \
    QLabel, QFileDialog
from PyQt5.QtCore import Qt
from pynput import keyboard


class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.hide()  # Start hidden
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()  # Start the keyboard listener

        # Network setup
        self.client_socket = None
        self.server_ip = '10.10.217.196'  # Change this to the server's IP
        self.server_port = 5001
        self.client_ip = None
        self.connect_to_server()

    def init_ui(self):
        self.setWindowTitle('Chat App')
        self.setGeometry(100, 100, 400, 600)

        # Set a solid background color with border and rounded corners
        self.setStyleSheet("""  
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30, 30, 30, 255), stop:1 rgba(50, 50, 50, 255));
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 10px;
            }
        """)

        # Set window flags to make it frameless and stay on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

        # Title
        title_label = QLabel('Chat')
        title_label.setStyleSheet("color: #FFFFFF; font-size: 24px;")
        main_layout.addWidget(title_label)

        # Chat display area
        self.chat_display = QListWidget()
        self.chat_display.setStyleSheet("""
            QListWidget {
                background-color: rgba(60, 63, 70, 200);
                color: white; 
                border: none; 
                padding: 10px;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.chat_display)

        # Input area
        self.input_area = QTextEdit()
        self.input_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(70, 73, 78, 200);
                color: white; 
                padding: 10px; 
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.input_area)

        # Button layout
        button_layout = QHBoxLayout()

        # Send button
        send_button = QPushButton('Send')
        send_button.setStyleSheet("background-color: #1abc9c; color: white; padding: 10px; border-radius: 5px;")
        send_button.clicked.connect(self.send_message)
        button_layout.addWidget(send_button)

        # Attach button
        attach_button = QPushButton('Attach')
        attach_button.setStyleSheet("background-color: #2980b9; color: white; padding: 10px; border-radius: 5px;")
        attach_button.clicked.connect(self.attach_file)
        button_layout.addWidget(attach_button)

        main_layout.addLayout(button_layout)

        # Add dummy groups for UI demonstration
        self.group_list = QListWidget()
        self.group_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(60, 63, 70, 200);
                color: white; 
                border: none; 
                padding: 10px;
                border-radius: 5px;
            }
        """)
        self.group_list.addItems(['Group 1', 'Group 2', 'Group 3'])  # Dummy groups
        main_layout.addWidget(self.group_list)

        # Set position of the window to the bottom right corner
        screen_geometry = QApplication.desktop().availableGeometry()
        self.move(screen_geometry.width() - self.width(), screen_geometry.height() - self.height())

        # Allow moving the window by clicking and dragging
        self.setMouseTracking(True)
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            self.move(event.globalPos() - self.old_pos)

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def on_key_press(self, key):
        try:
            if key == keyboard.Key.ctrl_r:  # Use F12 key to open the window
                print("Attempting to open chat window...")  # Debug message
                self.toggle_visibility()
        except AttributeError:
            pass

    def toggle_visibility(self):
        if self.isVisible():
            print("Hiding chat window...")  # Debug message
            self.hide()
        else:
            print("Showing chat window...")  # Debug message
            self.show()

    def send_message(self):
        message = self.input_area.toPlainText()
        if message and self.client_socket:
            # Send message to the server in the format "recipient_ip:message"
            recipient_ip = '192.168.56.1'  # Just an example, you could allow the user to select the recipient
            message_to_send = f"{recipient_ip}:{message}"
            self.client_socket.send(message_to_send.encode('utf-8'))
            self.chat_display.addItem(f"You: {message}")
            self.input_area.clear()

    def attach_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select a file", "", "All Files (*)", options=options)
        if file_name:
            self.chat_display.addItem(f"Attached: {file_name}")

    def connect_to_server(self):
        """Connects to the server and starts the listening thread."""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            print(f"Connected to server at {self.server_ip}:{self.server_port}")
            self.client_ip = self.client_socket.getsockname()[0]  # Get local IP address

            # Start the receiving thread to listen for incoming messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except ConnectionRefusedError:
            print("Server is not available. Please make sure the server is running.")

    def receive_messages(self):
        """Listens for messages from the server and updates the UI."""
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.chat_display.addItem(f"Received: {message}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Set a fusion style for better aesthetics
    window = ChatApp()
    window.show()  # Ensure window is initially shown for debug
    sys.exit(app.exec_())
