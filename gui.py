import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser, QProgressBar, QLabel, QRadioButton, QButtonGroup
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtGui import QColor
from backend.api import VoiceDictationTool
import argparse

class VoiceDictationToolGUI(QWidget):
    """GUI for Voice Dictation Tool with NER functionality."""

    def __init__(self, proper_nouns=False):
        super().__init__()
        self.dictation_tool = VoiceDictationTool(proper_nouns=proper_nouns)  # Instantiate the voice dictation tool
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

        # Bottom Layout for WER and Radio Buttons
        bottom_layout = QHBoxLayout()

        # WER display label
        self.wer_label = QLabel("WER: 0.00%", self)
        bottom_layout.addWidget(self.wer_label)

        # Radio buttons
        self.radio_button1 = QRadioButton("Repeat Only")
        self.radio_button2 = QRadioButton("Repeat + Noun Check")
        self.radio_button3 = QRadioButton("Noun Check Only")

        # Group radio buttons together for exclusive selection
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio_button1)
        self.radio_group.addButton(self.radio_button2)
        self.radio_group.addButton(self.radio_button3)

        # Add radio buttons to the bottom layout
        bottom_layout.addWidget(self.radio_button1)
        bottom_layout.addWidget(self.radio_button2)
        bottom_layout.addWidget(self.radio_button3)

        # Add the bottom layout to the main layout
        layout.addLayout(bottom_layout)

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

            # Use (index, word) tuple to uniquely identify each word instance
            word_key = (word_idx, clicked_word)

            # Toggle marking the word in red or removing the mark
            if word_key in self.marked_words:
                self.marked_words.remove(word_key)  # Unmark the word
            else:
                self.marked_words.add(word_key)  # Mark the word

        # Update the text box with the modified word list
        formatted_text = self.get_formatted_text(words)
        self.output_text.setHtml(formatted_text)

    def get_formatted_text(self, words):
        """Generate HTML for the transcription with marked words in red."""
        formatted_words = []
        for idx, word in enumerate(words):
            word_key = (idx, word)
            if word_key in self.marked_words:
                # Make the word clickable and apply red color if marked
                formatted_words.append(f'<a href="{idx}" style="color: red; text-decoration: underline;">{word}</a>')
            else:
                # Make the word clickable if not marked
                formatted_words.append(f'<a href="{idx}">{word}</a>')

        rate = len(self.marked_words)/len(words) * 100
        self.wer_label.setText(f'WER: {rate}')
        return ' '.join(formatted_words)

def parse_args():
    parser = argparse.ArgumentParser(description="Voice Dictation Tool")
    parser.add_argument('--proper_nouns', action='store_true', 
                        help="Enable proper noun playback after transcription")
    return parser.parse_args()

# Main execution for running the GUI
if __name__ == "__main__":
    args = parse_args()
    app = QApplication(sys.argv)
    gui = VoiceDictationToolGUI(proper_nouns=args.proper_nouns)
    gui.show()
    sys.exit(app.exec_())