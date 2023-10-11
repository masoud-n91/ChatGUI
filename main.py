import os

from PyQt5.QtWidgets import QMainWindow, QApplication
from ctransformers import AutoModelForCausalLM

from GUI import Ui_MainWindow

#import library

import speech_recognition as sr
import pyttsx3


###############################################################################
# The Main Window
###############################################################################
class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.r = sr.Recognizer()

        model_id = "TheBloke/Llama-2-7B-chat-GGML"

        config = {'max_new_tokens': 64, 'repetition_penalty': 1.1,
          'temperature': 0.1, 'stream': True}
        
        self.engine = pyttsx3.init() # object creation

        """ RATE"""
        rate = self.engine.getProperty('rate')   # getting details of current speaking rate
        print (rate)                        #printing current voice rate
        self.engine.setProperty('rate', 125)     # setting up new voice rate


        """VOLUME"""
        volume = self.engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
        print (volume)                          #printing current volume level
        self.engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

        """VOICE"""
        voices = self.engine.getProperty('voices')       #getting details of current voice
        self.engine.setProperty('voice', voices[0].id)   #changing index, changes voices. 1 for female/ 0 for male

        self.llm = AutoModelForCausalLM.from_pretrained(
            model_id,
            model_type="llama",
            #lib='avx2', for cpu use
            gpu_layers=15, #110 for 7b, 130 for 13b
            **config
            )


        self.ui.sendButton.clicked.connect(self.sendMsg)
        self.ui.rec_btn.clicked.connect(self.listening)


    def listening(self):
        # Reading Microphone as source
        # listening the speech and store in audio_text variable

        with sr.Microphone(1) as source:
            print("Talk")
            self.r.adjust_for_ambient_noise(source)
            audio_text = self.r.listen(source, timeout=5, phrase_time_limit=5)
            print("Time over, thanks")
        # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
            
            try:
                self.prompt = self.r.recognize_google(audio_text)
                # using google speech recognition
                print("Text: "+ self.prompt)
            except:
                self.prompt = "Sorry, I did not get that"
                print(self.prompt)

            self.ui.inputLine.clear()
            self.ui.inputLine.setText(self.prompt)

    
    def sendMsg(self):
        text = self.ui.inputLine.text()
        tokens = self.llm.tokenize(text)
        asnwer = self.llm(text, stream=False)
        text = "\nRequest:\n" + text + "\n\nAnswer:\n" + asnwer
        self.ui.outputLine.insertPlainText(text)

        QApplication.processEvents()

        self.engine.say(asnwer)
        self.engine.runAndWait()
        self.engine.stop()
        

    def closeEvent(self, event):
        QApplication.quit()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
    










