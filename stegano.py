import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import base64

def encode_message(image_path, message):
    try:
        img = Image.open(image_path).convert("RGB")

        message_utf8 = message.encode('utf-8')  # Encode to UTF-8 FIRST
        encoded_message = base64.b64encode(message_utf8).decode('utf-8')

        binary_message = ''.join(format(ord(char), '08b') for char in encoded_message)

        if len(binary_message) + 8 > img.width * img.height * 3:  # +8 for null terminator
            raise ValueError("Message too large to fit in image.")

        index = 0
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = img.getpixel((x, y))

                if index < len(binary_message):
                    r = (r & ~1) | int(binary_message[index])
                    index += 1
                else:  # Add null terminator if message is shorter
                    r = (r & ~1)  # Clear LSB
                if index < len(binary_message):
                    g = (g & ~1) | int(binary_message[index])
                    index += 1
                else:
                    g = (g & ~1)
                if index < len(binary_message):
                    b = (b & ~1) | int(binary_message[index])
                    index += 1
                else:
                    b = (b & ~1)
                img.putpixel((x, y), (r, g, b))

        new_image_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if new_image_path:
            img.save(new_image_path)
            messagebox.showinfo("Success", "Message encoded and image saved!")

    except FileNotFoundError:
        messagebox.showerror("Error", "Image file not found.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def decode_message(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        binary_message = ""

        for y in range(img.height):
            for x in range(img.width):
                r, g, b = img.getpixel((x, y))
                binary_message += str(r & 1)
                binary_message += str(g & 1)
                binary_message += str(b & 1)

        null_index = binary_message.find('00000000')
        if null_index == -1:
          raise ValueError("Null terminator not found. Corrupted image?")
        binary_message = binary_message[:null_index]

        decoded_message = ""
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i + 8]
            decoded_message += chr(int(byte, 2))

        decoded_message = base64.b64decode(decoded_message).decode('utf-8')
        return decoded_message

    except FileNotFoundError:
        messagebox.showerror("Error", "Image file not found.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def decode_message(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        binary_message = ""

        for y in range(img.height):
            for x in range(img.width):
                r, g, b = img.getpixel((x, y))
                binary_message += str(r & 1)
                binary_message += str(g & 1)
                binary_message += str(b & 1)
        
        #Remove padding if any.
        binary_message = binary_message[:binary_message.find('00000000')] #Stop at the first null byte which signifies the end of the message

        # Convert binary to text
        decoded_message = ""
        for i in range(0, len(binary_message), 8):
          byte = binary_message[i:i+8]
          decoded_message += chr(int(byte, 2))

        decoded_message = base64.b64decode(decoded_message).decode('utf-8') # Decode base64 

        return decoded_message

    except FileNotFoundError:
        messagebox.showerror("Error", "Image file not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}") # Handle other errors


def open_image_encode():
    path = filedialog.askopenfilename()
    if path:
        global encode_image_path
        encode_image_path = path
        encode_image_label.config(text=path)


def open_image_decode():
    path = filedialog.askopenfilename()
    if path:
        global decode_image_path
        decode_image_path = path
        decode_image_label.config(text=path)

def start_encoding():
  message = encode_text.get("1.0", tk.END).strip() #Get the message from the text widget.
  encode_message(encode_image_path, message)

def start_decoding():
    decoded_message = decode_message(decode_image_path)
    if decoded_message:
        decode_text.delete("1.0", tk.END)  # Clear previous text
        decode_text.insert(tk.END, decoded_message)


# GUI setup
window = tk.Tk()
window.title("Steganography Tool")

# Encode Frame
encode_frame = tk.LabelFrame(window, text="Encode")
encode_frame.pack(pady=10, padx=10, fill=tk.X)

encode_image_label = tk.Label(encode_frame, text="No image selected")
encode_image_label.pack()
encode_button = tk.Button(encode_frame, text="Select Image", command=open_image_encode)
encode_button.pack()

encode_text_label = tk.Label(encode_frame, text="Enter message:")
encode_text_label.pack()

encode_text = tk.Text(encode_frame, height=5)
encode_text.pack()

encode_start_button = tk.Button(encode_frame, text="Encode", command=start_encoding)
encode_start_button.pack()

# Decode Frame
decode_frame = tk.LabelFrame(window, text="Decode")
decode_frame.pack(pady=10, padx=10, fill=tk.X)

decode_image_label = tk.Label(decode_frame, text="No image selected")
decode_image_label.pack()
decode_button = tk.Button(decode_frame, text="Select Image", command=open_image_decode)
decode_button.pack()

decode_text = tk.Text(decode_frame, height=5)
decode_text.pack()

decode_start_button = tk.Button(decode_frame, text="Decode", command=start_decoding)
decode_start_button.pack()

encode_image_path = "" #Store the path of the image to encode
decode_image_path = "" #Store the path of the image to decode


window.mainloop()