import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk

END = "1111111111111110"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = TkinterDnD.Tk()
app.title("hiimg")
app.geometry("760x220")
app.iconbitmap("icon.ico")
app.configure(bg="#1e1e1e")

img_path = None
preview_img = None


def to_bin(t):
    return "".join(format(ord(c), "08b") for c in t)

def to_txt(b):
    return "".join(chr(int(b[i:i+8], 2)) for i in range(0, len(b), 8))


def set_image(path):
    global img_path, preview_img

    img_path = path
    im = Image.open(path)
    im.thumbnail((200, 200))

    preview_img = ImageTk.PhotoImage(im)
    preview.configure(image=preview_img, text="")

    update_capacity()


def update_capacity():
    if not img_path:
        cap.configure(text="capacity. -")
        return

    im = Image.open(img_path)
    w, h = im.size
    cap.configure(text=f"capacity. ~{(w*h*3)//8 - len(END)} chars")


def drop(event):
    set_image(event.data.strip("{}"))


def load():
    p = filedialog.askopenfilename(filetypes=[("images", "*.png *.jpg *.jpeg")])
    if p:
        set_image(p)


def inject():
    if not img_path:
        status.configure(text="no image")
        return

    msg = box.get("1.0", "end").strip()
    if not msg:
        status.configure(text="empty")
        return

    im = Image.open(img_path).convert("RGB")
    pixels = list(im.getdata())

    data = to_bin(msg) + END
    i = 0
    out = []

    for r, g, b in pixels:
        if i < len(data):
            r = (r & ~1) | int(data[i]); i += 1
        if i < len(data):
            g = (g & ~1) | int(data[i]); i += 1
        if i < len(data):
            b = (b & ~1) | int(data[i]); i += 1

        out.append((r, g, b))

    im.putdata(out)

    save = filedialog.asksaveasfilename(defaultextension=".png")
    if save:
        im.save(save)

    status.configure(text="done")


def extract():
    if not img_path:
        status.configure(text="no image")
        return

    im = Image.open(img_path)
    pixels = list(im.getdata())

    bits = ""
    for r, g, b in pixels:
        bits += str(r & 1)
        bits += str(g & 1)
        bits += str(b & 1)

    end = bits.find(END)
    if end == -1:
        status.configure(text="nothing found")
        return

    msg = to_txt(bits[:end])
    box.delete("1.0", "end")
    box.insert("1.0", msg)
    status.configure(text="extracted")


def copy_text():
    app.clipboard_clear()
    app.clipboard_append(box.get("1.0", "end").strip())
    status.configure(text="copied")


def toggle_theme():
    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("Light")
        app.configure(bg="#f2f2f2")
    else:
        ctk.set_appearance_mode("Dark")
        app.configure(bg="#1e1e1e")

def clear_text():
    box.delete("1.0", "end")
    status.configure(text="cleared")

app.minsize(600, 400)

main = ctk.CTkFrame(app, fg_color="#222222")
main.pack(fill="both", expand=True, padx=8, pady=8)

left = ctk.CTkFrame(main, width=180, fg_color="#2a2a2a")
left.pack(side="left", fill="y", padx=(0, 8))

right = ctk.CTkFrame(main, fg_color="#2a2a2a")
right.pack(side="left", fill="both", expand=True)

preview = ctk.CTkLabel(left, text="drop image")
preview.pack(pady=10)

preview.drop_target_register(DND_FILES)
preview.dnd_bind("<<Drop>>", drop)

ctk.CTkButton(left, text="load", command=load, fg_color="#3a3a3a").pack(pady=5)

cap = ctk.CTkLabel(left, text="capacity. -")
cap.pack(pady=5)


box = ctk.CTkTextbox(right, height=180, fg_color="#1c1c1c")
box.pack(padx=10, pady=10, fill="x")

btns = ctk.CTkFrame(right, fg_color="#2a2a2a")
btns.pack(pady=5)

ctk.CTkButton(btns, text="inject", command=inject, fg_color="#444").pack(side="left", padx=5)
ctk.CTkButton(btns, text="extract", command=extract, fg_color="#444").pack(side="left", padx=5)
ctk.CTkButton(btns, text="copy", command=copy_text, fg_color="#444").pack(side="left", padx=5)
ctk.CTkButton(btns, text="clear", command=clear_text, fg_color="#444").pack(side="left", padx=5)

status = ctk.CTkLabel(app, text="")
status.pack(pady=5)

app.mainloop()
