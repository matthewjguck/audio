import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QProgressBar
from PyQt5.QtCore import QTimer
import backend

class VoiceDictationToolGUI(QWidget):
    """GUI for Voice Dictation Tool with NER functionality."""

    def __init__(self):
        super().__init__()
        self.dictation_tool = backend.VoiceDictationTool()  # Instantiate the voice dictation tool
        self.is_recording = False  # Track whether we are recording
        self.initUI()

    def initUI(self):
        """Set up the GUI layout."""
        self.setWindowTitle('Voice Dictation Tool')

        # Main layout
        layout = QVBoxLayout()

        # Output text box
        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)  # Set to read-only, as it's only for output
        self.output_text.setPlaceholderText("Transcribed text will appear here...")
        layout.addWidget(self.output_text)

        # Start/Stop button
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.on_start_stop_click)  # Connect to start/stop recording
        layout.addWidget(self.start_button)

        # Busy indicator (Progress bar used as a visual indicator)
        self.busy_indicator = QProgressBar(self)
        self.busy_indicator.setRange(0, 0)  # Makes it indefinite (busy indicator)
        self.busy_indicator.setVisible(False)  # Hide it initially
        layout.addWidget(self.busy_indicator)

        # Set the layout to the window
        self.setLayout(layout)
        self.setGeometry(300, 300, 400, 300)

    def on_start_stop_click(self):
        """Handle the Start/Stop button click."""
        if self.is_recording:
            # If already recording, stop the recording
            self.on_stop_click()
        else:
            # If not recording, start the recording
            self.on_start_click()

    def on_start_click(self):
        """Handle the Start button click to begin recording."""
        self.is_recording = True
        self.start_button.setText('Stop')  # Change button text to "Stop"
        self.busy_indicator.setVisible(True)  # Show busy indicator

        # Start the voice recording
        self.dictation_tool.start_recording()

    def on_stop_click(self):
        """Handle the Stop button click to stop recording."""
        self.is_recording = False
        self.start_button.setEnabled(False)  # Disable button to prevent multiple clicks

        self.on_recording_finished()

    def on_recording_finished(self):
        """Handle the process after recording is finished."""
        self.dictation_tool.stop_recording()  # Stop recording and transcribe
        transcription = self.dictation_tool.transcription  # Get the transcribed text

        # Update the text box with the transcription
        self.output_text.setPlainText(transcription)

        # Hide the busy indicator and re-enable the button
        self.busy_indicator.setVisible(False)
        self.start_button.setText('Start')  # Change button text back to "Start"
        self.start_button.setEnabled(True)  # Re-enable the button


# Main execution for running the GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = VoiceDictationToolGUI()
    gui.show()
    sys.exit(app.exec_())