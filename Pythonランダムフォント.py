import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import os
import random
from reportlab.pdfgen import canvas

# 定数
MAX_FONTS = 10
WIDTH = 1000
HEIGHT = 200
FONT_SIZE = 48

# 状態
font_files = []
style_flags = {
    "bold": False,
    "italic": False,
    "underline": False,
    "strikethrough": False
}

def add_fonts():
    global font_files
    paths = filedialog.askopenfilenames(
        title="フォントファイルを選択",
        filetypes=[("Font files", "*.ttf *.otf")]
    )
    for path in paths:
        if len(font_files) < MAX_FONTS:
            font_files.append(path)
    label_fonts.config(text=f"選択中フォント数: {len(font_files)}")

def update_styles():
    style_flags["bold"] = var_bold.get()
    style_flags["italic"] = var_italic.get()
    style_flags["underline"] = var_underline.get()
    style_flags["strikethrough"] = var_strike.get()

def generate_image(text):
    if not font_files:
        messagebox.showwarning("フォント未選択", "フォントを1つ以上選択してください。")
        return None

    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))  # 透明背景
    draw = ImageDraw.Draw(image)
    x = 10
    y = 60

    for char in text:
        font_path = random.choice(font_files)
        try:
            base_font = ImageFont.truetype(font_path, FONT_SIZE)
        except IOError:
            messagebox.showerror("フォント読み込みエラー", f"読み込み失敗: {font_path}")
            return None

        bbox = draw.textbbox((0, 0), char, font=base_font)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]


        # 太字（擬似）
        if style_flags["bold"]:
            for offset in [(1, 0), (0, 1), (1, 1)]:
                draw.text((x + offset[0], y + offset[1]), char, fill="black", font=base_font)

        # 斜体（擬似）
        if style_flags["italic"]:
            draw.text((x + 2, y - 2), char, fill="gray", font=base_font)

        # 通常テキスト
        draw.text((x, y), char, fill="black", font=base_font)

        # アンダーライン
        if style_flags["underline"]:
            draw.line((x, y + char_height + 5, x + char_width, y + char_height + 5), fill="black", width=2)

        # 取り消し線
        if style_flags["strikethrough"]:
            draw.line((x, y + char_height // 2, x + char_width, y + char_height // 2), fill="black", width=2)

        x += char_width + 5

    return image

def export_image(img, filetype, path):
    if filetype in ["PNG", "JPEG"]:
        img.save(path, filetype)
    elif filetype == "PDF":
        img_path = path.replace(".pdf", ".png")
        img.save(img_path, "PNG")
        c = canvas.Canvas(path, pagesize=(WIDTH, HEIGHT))
        c.drawImage(img_path, 0, 0, width=WIDTH, height=HEIGHT)
        c.save()
        os.remove(img_path)

def on_generate():
    update_styles()
    text = entry.get()
    if len(text) == 0 or len(text) > 20:
        messagebox.showwarning("文字数制限", "1〜20文字で入力してください。")
        return

    img = generate_image(text)
    if img:
        filetype = export_var.get()
        ext = "." + filetype.lower()
        filepath = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[(filetype, "*" + ext)])
        if filepath:
            export_image(img, filetype, filepath)
            messagebox.showinfo("完了", f"保存しました：\n{filepath}")
            img.show()

def on_generate_10():
    update_styles()
    text = entry.get()
    if len(text) == 0 or len(text) > 20:
        messagebox.showwarning("文字数制限", "1〜20文字で入力してください。")
        return
    if not font_files:
        messagebox.showwarning("フォント未選択", "フォントを1つ以上選択してください。")
        return

    filetype = export_var.get()
    ext = "." + filetype.lower()
    folder = filedialog.askdirectory(title="保存先フォルダを選択")
    if not folder:
        return

    base_name = filedialog.asksaveasfilename(
        title="ファイル名のベース（名前）を入力",
        defaultextension=ext,
        filetypes=[(filetype, "*" + ext)]
    )
    if not base_name:
        return

    base_name = os.path.splitext(os.path.basename(base_name))[0]
    saved_paths = []

    for i in range(10):
        img = generate_image(text)
        if img:
            path = os.path.join(folder, f"{base_name}_{i + 1}{ext}")
            export_image(img, filetype, path)
            saved_paths.append(path)

    messagebox.showinfo("完了", f"{len(saved_paths)}ファイルを保存しました。")
    os.startfile(folder)

# GUI構築
root = tk.Tk()
root.title("新聞風タイトル画像生成ツール（完全版）")

tk.Label(root, text="タイトル文字列（20字以内）").pack()
entry = tk.Entry(root, font=("Arial", 16), width=30)
entry.pack(pady=5)

tk.Button(root, text="フォントを追加（最大10）", command=add_fonts).pack()
label_fonts = tk.Label(root, text="選択中フォント数: 0")
label_fonts.pack()

frame_style = tk.Frame(root)
frame_style.pack(pady=5)

var_bold = tk.BooleanVar()
tk.Checkbutton(frame_style, text="太字", variable=var_bold).grid(row=0, column=0)

var_italic = tk.BooleanVar()
tk.Checkbutton(frame_style, text="斜体", variable=var_italic).grid(row=0, column=1)

var_underline = tk.BooleanVar()
tk.Checkbutton(frame_style, text="アンダーライン", variable=var_underline).grid(row=0, column=2)

var_strike = tk.BooleanVar()
tk.Checkbutton(frame_style, text="取り消し線", variable=var_strike).grid(row=0, column=3)

export_var = tk.StringVar(value="PNG")
tk.Label(root, text="出力形式を選択").pack()
tk.OptionMenu(root, export_var, "PNG", "JPEG", "PDF").pack(pady=5)

tk.Button(root, text="画像生成・保存（1回）", command=on_generate).pack(pady=5)
tk.Button(root, text="画像生成・保存（10回連続）", command=on_generate_10, bg="#e0e0e0").pack(pady=5)

root.mainloop()
