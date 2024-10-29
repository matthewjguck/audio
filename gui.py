import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextBrowser, QProgressBar
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtGui import QColor
from backend.api import VoiceDictationTool

class VoiceDictationToolGUI(QWidget):
    """GUI for Voice Dictation Tool with NER functionality."""

    def __init__(self):
        super().__init__()
        self.dictation_tool = VoiceDictationTool()  # Instantiate the voice dictation tool
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

        # Proper nouns display area
        self.proper_nouns_text = QTextBrowser(self)
        self.proper_nouns_text.setPlaceholderText("Proper nouns will appear here...")
        self.proper_nouns_text.setOpenExternalLinks(False)
        layout.addWidget(self.proper_nouns_text)

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
        self.setGeometry(300, 300, 400, 400)

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

        # Stop the recording in the background with a delay
        QTimer.singleShot(100, self.on_recording_finished)  # Delay of 100 ms before processing

    def on_recording_finished(self):
        """Handle the process after recording is finished."""
        # Stop recording and get the transcription and proper nouns
        transcription, proper_nouns = self.dictation_tool.stop_recording()

        # Format transcription into clickable words
        formatted_text = self.format_transcription(transcription) if transcription else "Transcription failed."

        # Update the text box with the formatted clickable transcription
        self.output_text.setHtml(formatted_text)

        # Display proper nouns below transcription
        proper_nouns_text = ', '.join(proper_nouns) if proper_nouns else "No proper nouns detected."
        self.proper_nouns_text.setText(proper_nouns_text)

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