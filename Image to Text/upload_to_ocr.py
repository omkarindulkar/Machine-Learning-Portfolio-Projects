# To setup pytesseract
# https://tesseract-ocr.github.io/tessdoc/Home.html
# https://github.com/UB-Mannheim/tesseract/wiki
import os
from flask import Flask, request
import matplotlib.pyplot as plt 
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = (r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe')

UPLOAD_FOLDER = './upload'
src_path = './upload/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        file1.save(path)
        image = cv2.imread(src_path + file1.filename)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        threshold_img = cv2.threshold(
                        gray_image, 0, 
                        255, cv2.THRESH_BINARY |
                        cv2.THRESH_OTSU)[1]


        from pytesseract import Output
        custom_config = r'--oem 3 --psm 6'
        details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang='eng')
        total_boxes = len(details['text'])
        for sequence_number in range(total_boxes):
            if int(details['conf'][sequence_number]) >30:
                (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number],  details['height'][sequence_number])
                threshold_img = cv2.rectangle(threshold_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        parse_text = []
        word_list = []
        last_word = ''
        for word in details['text']:
            if word!='':
                word_list.append(word)
                last_word = word
            if (last_word!='' and word == '') or (word==details['text'][-1]):
                parse_text.append(word_list)
                word_list = []

        for text in parse_text:
            print(text)
        text = ''.join(map(str, parse_text))
        unwanted_char = ['[',']',"'",",","  "]
        for i in unwanted_char:
            text = text.replace(i, ' ')
            text = text.replace(i, ' ')
        return ("Extracted Text:" + text)

    return '''
    <h1>Upload new File</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file1">
      <input type="submit">
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)