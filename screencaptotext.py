import messagebox
import ocr
import dlimage

def convert(img):
    if isinstance(img, str):
        valid = validate_url(img)
        pil_img = dlimage.get(img)
    else:
        pil_img = img
    
    text_lines = ocr.process(pil_img)
    message_boxes = messagebox.find(pil_img)

    messages = []
    for box in message_boxes:
        message = {'box': box, 'text': ""}
        for line in text_lines:
            if text_line_inside_box(line, box):
                message['text'] += line['text'] + "\n"
        
        if message['text']:
            messages.append(message)

    return messages

def text_line_inside_box(line, box):
    line_x1 = line['x1']
    line_y1 = line['y1']
    line_x2 = line['x2']
    line_y2 = line['y2']
    box_x1, box_y1, box_x2, box_y2 = box

    return (box_x1+8 < line_x1 < line_x2 < box_x2-8 and box_y1+8 < line_y1 < line_y2 < box_y2-8)


def validate_url(url):
    return True

if __name__ == "__main__":
    url = 'https://i.imgur.com/ub1JcdD.jpg'
    messages = convert(url)
    for msg in messages:
        print('----')
        print(msg['text'])