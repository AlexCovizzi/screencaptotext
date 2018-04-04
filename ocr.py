from PIL import Image
import cv2
import numpy as np
import pytesseract
from statistics import mode
import time

# img PIL Image
# bounds (X1, Y1, X2, Y2)
def process(pil_img, bounds = None):
    if bounds: pil_img = pil_img.crop(bounds)
    
    prep_img = preprocess(pil_img)
    string = pytesseract.image_to_boxes(prep_img, lang="eng", config='tessconfig')

    hsize = pil_img.size[1]
    chars = []
    rows = string.split("\n")
    for row in rows:
        tokens = row.split(" ")
        char = {'text':tokens[0], 'x1':int(tokens[1]), 'y1':hsize-int(tokens[4]), 'x2':int(tokens[3]), 'y2':hsize-int(tokens[2])}
        chars.append(char)
    chars = filter_chars(chars)
    words = chars_to_words(chars)
    lines = words_to_lines(words)

    prep_img.close()

    return lines


def preprocess(pil_img):
    cv_img = np.array(pil_img, dtype=np.uint8)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
    cv_img = contrast(cv_img)
    _,cv_img = cv2.threshold(cv_img, 200, 255, cv2.THRESH_TOZERO)
    return Image.fromarray(cv_img)

def contrast(cv_img, alpha=1.5, beta=-60.0):
    array_alpha = np.array([float(alpha)])
    array_beta = np.array([float(beta)])

    cv_img = cv2.add(cv_img, array_beta)
    cv_img = cv2.multiply(cv_img, array_alpha)
    
    return cv_img

def filter_chars(chars):
    filtered_chars = []
    for char in chars:
        w = char['x2'] - char['x1']
        h = char['y2'] - char['y1']
        if w < 40 and h < 40:
            filtered_chars.append(char)
    return filtered_chars

def chars_to_words(chars):
    words = [chars[0]]
    for char in chars[1:]:
        last = words[-1]
        if last['x2']-4 < char['x1'] < last['x2']+8 and ( last['y1']-12 < char['y1'] < last['y1']+12 or last['y2']-12 < char['y2'] < last['y2']+12 ):
            last['text'] += char['text']
            last['x2'] = char['x2']
            if char['y1'] < last['y1']:
                last['y1'] = char['y1']
        else:
            words.append(char)
 
    return words

def words_to_lines(words):
    lines = [words[0]]
    for word in words[1:]:
        last = lines[-1]
        if last['x2'] < word['x1'] < last['x2']+24 and ( last['y1']-12 < word['y1'] < last['y1']+12 or last['y2']-12 < word['y2'] < last['y2']+12 ):
            last['text'] += " "+word['text']
            last['x2'] = word['x2']
        else:
            lines.append(word)
    return lines

if __name__ == '__main__':
    import dlimage
    import messagebox

    url = "https://i.redd.it/rdz88lh48rp01.png"
    pil_img = dlimage.get(url)

    cv_img = np.array(pil_img, dtype=np.uint8)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
    
    lines = process(pil_img)
    for line in lines:
        print(line)

    cv2.imshow('img', cv2.resize(cv_img, (0,0), fx=0.4, fy=0.4))
    cv2.waitKey(0)