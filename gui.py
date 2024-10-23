import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextBrowser, QProgressBar
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtGui import QColor
import backend

class VoiceDictationToolGUI(QWidget):
    """GUI for Voice Dictation Tool with NER functionality."""

    def __init__(self):
        super().__init__()
        self.dictation_tool = backend.VoiceDictationTool()  # Instantiate the voice dictation tool
        self.is_recording = False  # Track whether we are recording
        self.initUI()
        self.marked_words = set()  # Set to track which words have been marked

    def initUI(self):
        """Set up the GUI layout."""
        self.setWindowTitle('Voice Dictation Tool')

        # Main layout
        layout = QVBoxLayout()

        # Output text box (QTextBrowser to support clickable text)
        self.output_text = QTextBrowser(self)
        self.output_text.setOpenExternalLinks(False)  # Disable external links
        self.output_text.setPlaceholderText("Transcribed text will appear here...")
        self.output_text.anchorClicked.connect(self.on_word_click)  # Connect word click handler
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

        # Split transcription into words and make them clickable
        formatted_text = self.format_transcription(transcription)

        # Update the text box with the formatted clickable transcription
        self.output_text.setHtml(formatted_text)

        # Hide the busy indicator and re-enable the button
        self.busy_indicator.setVisible(False)
        self.start_button.setText('Start')  # Change button text back to "Start"
        self.start_button.setEnabled(True)  # Re-enable the button

    def format_transcription(self, text):
        """Format the transcribed text to make each word clickable."""
        words = text.split()
        formatted_words = []

        # Wrap each word in a clickable <a> tag with a unique href
        for idx, word in enumerate(words):
            formatted_words.append(f'<a href="{idx}">{word}</a>')

        # Join the words back with spaces and return as HTML
        return ' '.join(formatted_words)

    def on_word_click(self, url):
        """Handle the event when a word is clicked."""
        word_idx = int(url.toString())  # Get the index of the clicked word
        words = self.output_text.toPlainText().split()

        if word_idx < len(words):
            clicked_word = words[word_idx]

            # Toggle marking the word in red
            if clicked_word not in self.marked_words:
                self.marked_words.add(clicked_word)
                words[word_idx] = f'<span style="color: red; text-decoration: underline;">{clicked_word}</span>'
            else:
                self.marked_words.remove(clicked_word)
                words[word_idx] = f'<a href="{word_idx}">{clicked_word}</a>'

        # Update the text box with the modified word list
        formatted_text = ' '.join(words)
        self.output_text.setHtml(formatted_text)

        # (Future) Connect to WER backend to handle error processing for the clicked word
        # Example: self.dictation_tool.mark_word_for_error(clicked_word)


# Main execution for running the GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = VoiceDictationToolGUI()
    gui.show()
    sys.exit(app.exec_())