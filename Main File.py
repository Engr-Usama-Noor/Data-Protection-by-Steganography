"""
    Steganography refers to encoding and decoding data into non-text files such as audio files, video files and images files

    In this project, we will only deal with encoding and decoding data in an image
"""

# Importing the necessary modules

import csv
from datetime import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import *
from tkinter import messagebox as mb
from PIL import Image

import os
print(os.getcwd())


def generate_data(pixels, data):
    data_in_binary = [format(ord(char), '08b') for char in data]
    data_len = len(data_in_binary)
    image_data = iter(pixels)

    for i in range(data_len):
        # Get next 3 pixels = 9 channels (R, G, B)
        pixel_values = []
        for _ in range(3):
            pixel_values.extend(next(image_data)[:3])

        # Modify the first 8 channels
        for j in range(8):
            if data_in_binary[i][j] == '0':
                pixel_values[j] = pixel_values[j] & ~1  # set LSB to 0
            else:
                pixel_values[j] = pixel_values[j] | 1   # set LSB to 1

        # Set the 9th channel LSB to indicate if it's the last character
        if i == data_len - 1:
            pixel_values[8] = pixel_values[8] | 1  # LSB = 1 (end)
        else:
            pixel_values[8] = pixel_values[8] & ~1  # LSB = 0

        yield tuple(pixel_values[0:3])
        yield tuple(pixel_values[3:6])
        yield tuple(pixel_values[6:9])



def encryption(img, data):
    # This method will encode data to the new image that will be created
    size = img.size[0]
    (x, y) = (0, 0)

    for pixel in generate_data(img.getdata(), data):
        img.putpixel((x, y), pixel)
        if size-1 == x:
            x = 0; y += 1
        else:
            x += 1

# Function to encrypt the data

def main_encryption(img, text, new_image_name, password):
    from cryptography.fernet import Fernet
    import base64
    import hashlib

    image = Image.open(img, 'r')

    if (len(text) == 0) or (len(img) == 0) or (len(new_image_name) == 0) or (len(password) == 0):
        mb.showerror("Error", 'All fields including password are required.')
        return

    # Hash password to 32-byte key
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
    fernet = Fernet(key)

    # Encrypt text
    try:
        encrypted_data = fernet.encrypt(text.encode()).decode()
    except Exception as e:
        mb.showerror("Error", f"Encryption failed: {str(e)}")
        return

    new_image = image.copy()
    encryption(new_image, encrypted_data)
    
    new_image_name += '.png'
    new_image.save(new_image_name, 'png')

    # Save password entry
    save_password_to_csv(new_image_name, password)

    mb.showinfo("Success", f"Image encoded and saved as {new_image_name}")


# Funtion to decrypt the data

def main_decryption(img, text_box, password):
    from cryptography.fernet import Fernet
    import base64
    import hashlib

    image = Image.open(img, 'r')
    data = ''
    image_data = iter(image.getdata())
    decoding = True

    while decoding:
        pixels = [value for value in next(image_data)[:3] + next(image_data)[:3] + next(image_data)[:3]]
        binary_string = ''

        for i in pixels[:8]:
            binary_string += '0' if i % 2 == 0 else '1'

        char = chr(int(binary_string, 2))
        if pixels[-1] % 2 != 0:
            decoding = False
        data += char

    # Attempt decryption
    try:
        key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
        fernet = Fernet(key)
        decrypted_text = fernet.decrypt(data.encode()).decode()
        text_box.config(state='normal')
        text_box.delete('1.0', END)
        text_box.insert(END, decrypted_text)
        text_box.config(state='disabled')
    except Exception as e:
        mb.showerror("Error", "Incorrect password or corrupted data.")


# Password saving process

def save_password_to_csv(image_name: str, password: str):
    with open('saved_keys.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), image_name, password])



# Creating the button functions
def encode_image():
    encode_wn = Toplevel(root)
    encode_wn.title("Stego by UHZH")
    encode_wn.geometry('620x350')
    encode_wn.resizable(0, 0)
    encode_wn.config(bg='AntiqueWhite')

    # Updated Heading and Branding
    Label(encode_wn, text='Stego by UHZH', font=("Comic Sans MS", 15, 'bold'), bg='AntiqueWhite', fg='#2c3e50').place(x=220, y=5)
    Label(encode_wn, text='Make any data secure', font=("Comic Sans MS", 10), bg='AntiqueWhite', fg='#34495e').place(x=230, y=35)
    Label(encode_wn, text='KFUEIT, RYK', font=("Times New Roman", 10, 'italic'), bg='AntiqueWhite', fg='#7f8c8d').place(x=260, y=55)

    Label(encode_wn, text='Enter the path to the image (with extension):', font=("Times New Roman", 13), bg='AntiqueWhite').place(x=10, y=90)

    img_path = Entry(encode_wn, width=40)
    img_path.place(x=360, y=90)

    def drop_encode_file(event):
        dropped_file = event.data.strip().replace('{', '').replace('}', '')
        img_path.delete(0, END)
        img_path.insert(0, dropped_file)

    img_path.drop_target_register(DND_FILES)
    img_path.dnd_bind('<<Drop>>', drop_encode_file)

    # Improved multi-line text box with margin from right edge
    Label(encode_wn, text='Enter the data to be encoded:', font=("Times New Roman", 13), bg='AntiqueWhite').place(x=10, y=130)

    text_frame = Frame(encode_wn, bg='AntiqueWhite')
    text_frame.place(x=360, y=130, width=245, height=70)

    text_to_be_encoded = Text(text_frame, wrap='word', font=("Times New Roman", 10))
    text_to_be_encoded.pack(side=LEFT, fill=BOTH, expand=True)

    text_scroll_y = Scrollbar(text_frame, orient=VERTICAL, command=text_to_be_encoded.yview)
    text_scroll_y.pack(side=RIGHT, fill=Y)

    text_to_be_encoded.config(yscrollcommand=text_scroll_y.set)


    Label(encode_wn, text='Enter the output file name (without extension):', font=("Times New Roman", 13), bg='AntiqueWhite').place(x=10, y=220)
    after_save_path = Entry(encode_wn, width=40)
    after_save_path.place(x=360, y=220)

    Label(encode_wn, text='Enter encryption password:', font=("Times New Roman", 13), bg='AntiqueWhite').place(x=10, y=260)
    password_entry = Entry(encode_wn, width=40, show='*')
    password_entry.place(x=360, y=260)

    Button(encode_wn, text='Encode the Image', font=('Helvetica', 12), bg='PaleTurquoise', command=lambda:
    main_encryption(img_path.get(), text_to_be_encoded.get("1.0", END).strip(), after_save_path.get(), password_entry.get())).place(x=240, y=300)



def decode_image():
    decode_wn = Toplevel(root)
    decode_wn.title("Decode an Image")
    decode_wn.geometry('600x360')
    decode_wn.resizable(0, 0)
    decode_wn.config(bg='Bisque')

    Label(decode_wn, text='Decode an Image', font=("Comic Sans MS", 15), bg='Bisque').place(x=220, rely=0)

    Label(decode_wn, text='Enter the path to the image (with extension):', font=("Times New Roman", 12), bg='Bisque').place(x=10, y=50)
    Label(decode_wn, text='Enter encryption password:', font=("Times New Roman", 12), bg='Bisque').place(x=10, y=90)

    img_entry = Entry(decode_wn, width=35)
    img_entry.place(x=350, y=50)

    def drop_decode_file(event):
        dropped_file = event.data.strip().replace('{', '').replace('}', '')
        img_entry.delete(0, END)
        img_entry.insert(0, dropped_file)

    img_entry.drop_target_register(DND_FILES)
    img_entry.dnd_bind('<<Drop>>', drop_decode_file)

    
    password_entry = Entry(decode_wn, width=35, show='*')
    password_entry.place(x=350, y=90)

    Label(decode_wn, text='Text that has been encoded in the image:', font=("Times New Roman", 12), bg='Bisque').place(x=180, y=130)

    text_box = Text(decode_wn, wrap='word', width=70, height=7)
    text_box.place(x=15, y=160)

    scroll_y = Scrollbar(decode_wn, orient='vertical', command=text_box.yview)
    scroll_y.place(x=575, y=160, height=115)
    text_box.configure(yscrollcommand=scroll_y.set)

    Button(decode_wn, text='Decode the Image', font=('Helvetica', 12), bg='PaleTurquoise', command=lambda:
    main_decryption(img_entry.get(), text_box, password_entry.get())).place(x=220, y=300)



# Initializing the window
root = TkinterDnD.Tk()
root.title('Project Gurukul Image Steganography')
root.geometry('300x200')
root.resizable(0, 0)
root.config(bg='NavajoWhite')

Label(root, text='Stego by UHZH', font=('Comic Sans MS', 16, 'bold'), bg='NavajoWhite', fg='#2c3e50').place(x=60, y=10)
Label(root, text='Make any data secure', font=('Comic Sans MS', 10), bg='NavajoWhite', fg='#34495e').place(x=80, y=45)
Label(root, text='KFUEIT, RYK', font=('Times New Roman', 10, 'italic'), bg='NavajoWhite', fg='#7f8c8d').place(x=100, y=65)


Button(root, text='Encode', width=25, font=('Times New Roman', 13), bg='SteelBlue', command=encode_image).place(
    x=30, y=90)

Button(root, text='Decode', width=25, font=('Times New Roman', 13), bg='SteelBlue', command=decode_image).place(
    x=30, y=140)

# Finalizing the window
root.update()
root.mainloop()