import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import hashlib
import base64
from stegano import lsb
from cryptography.fernet import Fernet, InvalidToken


#  Encryption Helpers

def get_fernet_key(password: str) -> bytes:
    """Derive a 32-byte Fernet key from a password using SHA-256."""
    raw = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(raw)


def encrypt_message(message: str, password: str) -> str:
    key = get_fernet_key(password)
    cipher = Fernet(key)
    return cipher.encrypt(message.encode()).decode()


def decrypt_message(token: str, password: str) -> str:
    key = get_fernet_key(password)
    cipher = Fernet(key)
    return cipher.decrypt(token.encode()).decode()



#  Colour & Font Tokens

BG_DARK    = "#0d1117"
BG_CARD    = "#161b22"
BG_INPUT   = "#21262d"
ACCENT     = "#58a6ff"
ACCENT2    = "#3fb950"
WARN       = "#f85149"
TEXT_PRI   = "#e6edf3"
TEXT_SEC   = "#8b949e"
BORDER     = "#30363d"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_SUB    = ("Segoe UI", 11)
FONT_LABEL  = ("Segoe UI", 10)
FONT_BTN    = ("Segoe UI", 10, "bold")
FONT_MONO   = ("Consolas", 10)


#  Global State

filename         = None
password_visible = False



#  Core Logic

def select_image():
    global filename
    path = filedialog.askopenfilename(
        title="Select PNG Image",
        filetypes=[("PNG files", "*.png")]
    )
    if not path:
        return
    filename = path

    try:
        img = Image.open(filename)
        w, h = img.size
        capacity = (w * h * 3) // 8 - 26   # approximate LSB capacity in bytes

        # Show thumbnail
        thumb = img.copy()
        thumb.thumbnail((320, 260))
        tk_img = ImageTk.PhotoImage(thumb)
        img_label.configure(image=tk_img, text="")
        img_label.image = tk_img

        # Update info bar
        name = os.path.basename(filename)
        info_var.set(f"  {name}   |   {w} x {h} px   |   Capacity approx {capacity:,} chars")
        capacity_var.set(capacity)
        update_char_counter()
        status("Image loaded successfully.", "ok")

    except Exception as e:
        messagebox.showerror("Error", f"Cannot open image:\n{e}")


def hide_message():
    if not filename:
        messagebox.showwarning("No Image", "Please select a PNG image first.")
        return

    message  = text_box.get("1.0", tk.END).strip()
    password = password_entry.get().strip()

    if not message:
        messagebox.showwarning("Empty Message", "Please type a message to hide.")
        return
    if not password:
        messagebox.showwarning("No Password", "Please enter a password.")
        return

    capacity = capacity_var.get()
    if capacity > 0 and len(message) > capacity:
        messagebox.showerror(
            "Message Too Long",
            f"Message ({len(message):,} chars) exceeds image capacity ({capacity:,} chars).\n"
            "Use a larger image or a shorter message."
        )
        return

    try:
        encrypted = encrypt_message(message, password)
        secret_img = lsb.hide(filename, encrypted)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            title="Save Stego Image"
        )
        if save_path:
            secret_img.save(save_path)
            status(f"Message hidden & saved to {os.path.basename(save_path)}", "ok")
            messagebox.showinfo("Success", f"Message hidden successfully!\nSaved to: {save_path}")
            clear_interface()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to hide message:\n{e}")
        status("Hide operation failed.", "err")


def reveal_message():
    if not filename:
        messagebox.showwarning("No Image", "Please select the stego PNG image first.")
        return

    password = password_entry.get().strip()
    if not password:
        messagebox.showwarning("No Password", "Please enter the password.")
        return

    try:
        raw = lsb.reveal(filename)
        if not raw:
            messagebox.showwarning("No Data", "No hidden message found in this image.")
            status("No hidden message found.", "warn")
            return

        message = decrypt_message(raw, password)
        status("Message revealed successfully.", "ok")
        show_reveal_popup(message)

    except InvalidToken:
        messagebox.showerror("Wrong Password", "Incorrect password! Cannot decrypt the message.")
        status("Incorrect password.", "err")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to reveal message:\n{e}")
        status("Reveal operation failed.", "err")



#  UI Helpers

def show_reveal_popup(message: str):
    """Display the revealed message in a modal popup."""
    popup = tk.Toplevel(root)
    popup.title("Revealed Message")
    popup.geometry("540x380")
    popup.configure(bg=BG_CARD)
    popup.resizable(False, False)
    popup.grab_set()   # modal

    tk.Label(popup, text="Revealed Message",
             bg=BG_CARD, fg=ACCENT, font=("Segoe UI", 15, "bold")).pack(pady=(20, 8))

    frame = tk.Frame(popup, bg=BORDER)
    frame.pack(padx=20, fill="both", expand=True)

    msg_text = tk.Text(frame, wrap="word", font=FONT_MONO,
                       bg=BG_INPUT, fg=TEXT_PRI, relief="flat",
                       padx=10, pady=10, bd=0)
    msg_text.insert("1.0", message)
    msg_text.configure(state="disabled")

    scrollbar = ttk.Scrollbar(frame, command=msg_text.yview)
    msg_text.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    msg_text.pack(fill="both", expand=True)

    btn_frame = tk.Frame(popup, bg=BG_CARD)
    btn_frame.pack(pady=12)

    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(message)
        copy_btn.configure(text="Copied!")
        popup.after(2000, lambda: copy_btn.configure(text="Copy to Clipboard"))

    copy_btn = tk.Button(btn_frame, text="Copy to Clipboard", command=copy_to_clipboard,
                         bg=ACCENT, fg="white", font=FONT_BTN,
                         relief="flat", padx=14, pady=6, cursor="hand2")
    copy_btn.pack(side="left", padx=8)

    tk.Button(btn_frame, text="Close", command=popup.destroy,
              bg=BG_INPUT, fg=TEXT_PRI, font=FONT_BTN,
              relief="flat", padx=14, pady=6, cursor="hand2").pack(side="left", padx=8)


def toggle_password():
    global password_visible
    password_visible = not password_visible
    password_entry.configure(show="" if password_visible else "*")
    eye_btn.configure(text="Hide" if password_visible else "Show")


def clear_interface():
    text_box.delete("1.0", tk.END)
    password_entry.delete(0, tk.END)
    img_label.configure(image="", text="No image selected\nClick 'Select Image' to begin")
    img_label.image = None
    info_var.set("")
    char_var.set("Characters: 0")
    capacity_var.set(0)
    global filename
    filename = None
    status("Interface cleared.", "ok")


def update_char_counter(event=None):
    count = len(text_box.get("1.0", tk.END).strip())
    cap   = capacity_var.get()
    char_var.set(f"Characters: {count:,}")
    if cap > 0:
        if count > cap:
            char_counter_lbl.configure(fg=WARN)
        elif count > cap * 0.8:
            char_counter_lbl.configure(fg="#d29922")
        else:
            char_counter_lbl.configure(fg=TEXT_SEC)


def status(msg: str, level: str = "ok"):
    colours = {"ok": ACCENT2, "err": WARN, "warn": "#d29922"}
    status_lbl.configure(text=msg, fg=colours.get(level, TEXT_SEC))


#  Build UI

root = tk.Tk()
root.title("HideX Pro - Image Steganography")
root.geometry("1060x780")
root.minsize(900, 680)
root.configure(bg=BG_DARK)

# ── Configure ttk style ──────────────────────
style = ttk.Style()
style.theme_use("clam")
style.configure("Vertical.TScrollbar",
                background=BG_INPUT, troughcolor=BG_CARD,
                arrowcolor=TEXT_SEC, bordercolor=BG_CARD)

# ── Title bar ────────────────────────────────
title_bar = tk.Frame(root, bg=BG_DARK)
title_bar.pack(fill="x", padx=24, pady=(18, 0))

tk.Label(title_bar, text="HideX", bg=BG_DARK,
         fg=ACCENT, font=("Segoe UI", 28, "bold")).pack(side="left")
tk.Label(title_bar, text=" Pro", bg=BG_DARK,
         fg=ACCENT2, font=("Segoe UI", 28, "bold")).pack(side="left")
tk.Label(title_bar, text="  -  Image Steganography Tool",
         bg=BG_DARK, fg=TEXT_SEC, font=("Segoe UI", 13)).pack(side="left", pady=6)

tk.Label(title_bar, text="AES-256 Encrypted",
         bg=BG_DARK, fg=ACCENT2, font=("Segoe UI", 10)).pack(side="right", pady=6)

ttk.Separator(root).pack(fill="x", padx=24, pady=10)

# ── Main layout: left + right columns ────────
main = tk.Frame(root, bg=BG_DARK)
main.pack(fill="both", expand=True, padx=24, pady=0)
main.columnconfigure(0, weight=1)
main.columnconfigure(1, weight=1)
main.rowconfigure(0, weight=1)

# ───── LEFT: Image panel ─────────────────────
left = tk.Frame(main, bg=BG_CARD, bd=0, relief="flat")
left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)

tk.Label(left, text="Image Preview", bg=BG_CARD,
         fg=TEXT_SEC, font=FONT_LABEL, anchor="w").pack(fill="x", padx=14, pady=(12, 4))

img_frame = tk.Frame(left, bg=BG_INPUT, bd=0)
img_frame.pack(padx=14, fill="both", expand=True)

img_label = tk.Label(img_frame,
                     text="No image selected\nClick 'Select Image' to begin",
                     bg=BG_INPUT, fg=TEXT_SEC, font=("Segoe UI", 11),
                     justify="center")
img_label.pack(expand=True, fill="both", padx=4, pady=4)

info_var = tk.StringVar(value="")
tk.Label(left, textvariable=info_var, bg=BG_CARD,
         fg=TEXT_SEC, font=("Segoe UI", 9), anchor="w",
         wraplength=400).pack(fill="x", padx=14, pady=(6, 4))

tk.Button(left, text="Select PNG Image", command=select_image,
          bg=ACCENT, fg="white", font=FONT_BTN,
          relief="flat", padx=12, pady=8, cursor="hand2",
          activebackground="#1f6feb", activeforeground="white"
          ).pack(padx=14, pady=(4, 14), fill="x")

# ───── RIGHT: Controls panel ──────────────────
right = tk.Frame(main, bg=BG_CARD, bd=0, relief="flat")
right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=4)

tk.Label(right, text="Secret Message", bg=BG_CARD,
         fg=TEXT_SEC, font=FONT_LABEL, anchor="w").pack(fill="x", padx=14, pady=(12, 4))

text_frame = tk.Frame(right, bg=BORDER)
text_frame.pack(padx=14, fill="both", expand=True)

text_box = tk.Text(text_frame, height=8, font=FONT_MONO, wrap="word",
                   bg=BG_INPUT, fg=TEXT_PRI, insertbackground=ACCENT,
                   relief="flat", bd=0, padx=8, pady=8,
                   selectbackground=ACCENT, selectforeground="white")
text_box.bind("<KeyRelease>", update_char_counter)

txt_scroll = ttk.Scrollbar(text_frame, command=text_box.yview)
text_box.configure(yscrollcommand=txt_scroll.set)
txt_scroll.pack(side="right", fill="y")
text_box.pack(fill="both", expand=True)

char_var = tk.StringVar(value="Characters: 0")
capacity_var = tk.IntVar(value=0)
char_counter_lbl = tk.Label(right, textvariable=char_var,
                             bg=BG_CARD, fg=TEXT_SEC, font=("Segoe UI", 9), anchor="e")
char_counter_lbl.pack(fill="x", padx=14, pady=(2, 8))

# ── Password ──
tk.Label(right, text="Password", bg=BG_CARD,
         fg=TEXT_SEC, font=FONT_LABEL, anchor="w").pack(fill="x", padx=14, pady=(4, 4))

pw_frame = tk.Frame(right, bg=BORDER)
pw_frame.pack(padx=14, fill="x")

password_entry = tk.Entry(pw_frame, font=("Segoe UI", 12), show="*",
                          bg=BG_INPUT, fg=TEXT_PRI, insertbackground=ACCENT,
                          relief="flat", bd=0)
password_entry.pack(side="left", fill="both", expand=True, padx=(8, 0), ipady=8)

eye_btn = tk.Button(pw_frame, text="Show", command=toggle_password,
                    bg=BG_INPUT, fg=TEXT_SEC, font=("Segoe UI", 9),
                    relief="flat", bd=0, cursor="hand2", padx=8)
eye_btn.pack(side="right")

tk.Label(right, text="Password is used for AES-256 encryption and is never stored.",
         bg=BG_CARD, fg=TEXT_SEC, font=("Segoe UI", 8), anchor="w",
         wraplength=380).pack(fill="x", padx=14, pady=(4, 12))

# ── Action Buttons ──
btn_frame = tk.Frame(right, bg=BG_CARD)
btn_frame.pack(padx=14, fill="x", pady=(4, 6))
btn_frame.columnconfigure(0, weight=1)
btn_frame.columnconfigure(1, weight=1)

tk.Button(btn_frame, text="Hide Message", command=hide_message,
          bg="#1f6feb", fg="white", font=FONT_BTN,
          relief="flat", padx=10, pady=10, cursor="hand2",
          activeforeground="white"
          ).grid(row=0, column=0, padx=4, pady=4, sticky="ew")

tk.Button(btn_frame, text="Reveal Message", command=reveal_message,
          bg="#238636", fg="white", font=FONT_BTN,
          relief="flat", padx=10, pady=10, cursor="hand2",
          activeforeground="white"
          ).grid(row=0, column=1, padx=4, pady=4, sticky="ew")

tk.Button(btn_frame, text="Clear All", command=clear_interface,
          bg="#6e40c9", fg="white", font=FONT_BTN,
          relief="flat", padx=10, pady=10, cursor="hand2",
          activeforeground="white"
          ).grid(row=1, column=0, padx=4, pady=4, sticky="ew")

# ── Status bar ──────────────────────────────────
status_lbl = tk.Label(root, text="Welcome to HideX Pro - Select an image to begin.",
                      bg=BG_DARK, fg=TEXT_SEC, font=("Segoe UI", 9), anchor="w")
status_lbl.pack(fill="x", padx=26, pady=(4, 2))

ttk.Separator(root).pack(fill="x", padx=24)

tk.Label(root,
         text="HideX Pro  |  MCA Mini Project  |  LSB Steganography + AES-256 Encryption",
         bg=BG_DARK, fg=TEXT_SEC, font=("Segoe UI", 8)).pack(pady=(4, 8))

# ─────────────────────────────────────────────
root.mainloop()
