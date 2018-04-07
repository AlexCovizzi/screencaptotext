import numpy as np
import cv2
import time
import pytesseract
from PIL import Image

def find(pil_img):
    cv_img = np.array(pil_img, dtype=np.uint8)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)

    prep_img = preprocess(cv_img)
    boxes = find_bounding_boxes(prep_img)
    # sort by y1
    boxes.sort(key=lambda box: box['y1'])
    
    return boxes

def preprocess(cv_img):
    # preprocess
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    cv_img = cv2.GaussianBlur(cv_img, (7,7), 0)
    cv_img = contrast(cv_img, 1.455, -80)
    cv_img = cv2.Canny(cv_img, 10, 40)
    cv_img = cv2.GaussianBlur(cv_img, (7,7), 0)
    _,cv_img = cv2.threshold(cv_img, 40, 255, cv2.THRESH_BINARY)
    return cv_img

def find_bounding_boxes(cv_img):
    boxes = []
    _,contours,_ = cv2.findContours(cv_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # close every contour
    for i, cnt in enumerate(contours):
        contours[i] = cv2.convexHull(cnt)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        bounding_rect = np.array([[x, y], [x+w, y], [x+w, y+h], [x, y+h]])
        if w > 28 and h > 28 and is_contour_mostly_rectangular(cnt, bounding_rect):
            #cv2.drawContours(cv_img, [contours[parent]], 0, (0,255,0), 3)
            box = {'x1': x, 'y1':y, 'x2': x+w, 'y2':y+h}
            boxes.append(box)

    return boxes

def is_contour_mostly_rectangular(cnt, bounding_rect):
    ret = cv2.matchShapes(cnt, bounding_rect, 1, 0.0)

    vertical = 0
    horizontal = 0
    last_x, last_y = cnt[0][0]
    for pt in cnt[1:]:
        x, y = pt[0]
        if last_x-4 < x < last_x+4:
            v = abs(last_y-y)
            if v > vertical: vertical = v
        if last_y-2 < y < last_y+2:
            h = abs(last_x-x)
            if h > horizontal: horizontal = h
        last_x = x
        last_y = y

    return (ret < 0.2 and vertical > 6 and horizontal > 24)

def contrast(cv_img, alpha=1.5, beta=-60.0):
    array_alpha = np.array([float(alpha)])
    array_beta = np.array([float(beta)])

    cv_img = cv2.add(cv_img, array_beta)
    cv_img = cv2.multiply(cv_img, array_alpha)
    
    return cv_img

if __name__ == '__main__':
    import dlimage
    import pytesseract

    urls = ["https://i.redd.it/harvn2jkxcq01.jpg"]
    
    for url in urls:
        pil_img = dlimage.get(url)

        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        boxes = find(pil_img)

        for box in boxes:
            x1, y1, x2, y2 = (box['x1'], box['y1'], box['x2'], box['y2'])
            bounding_rect = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
            cv2.drawContours(cv_img, [bounding_rect], 0, (0,255,0), 3)

        cv2.imshow('img', cv2.resize(cv_img, (0,0), fx=0.4, fy=0.4))
        cv2.waitKey(0)