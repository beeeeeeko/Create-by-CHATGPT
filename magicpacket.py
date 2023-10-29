import tkinter as tk
import socket
import binascii
from tkinter import messagebox
import configparser

# 設定ファイルのパス
config_file = "magic_packet_config.ini"

# 更新設定一覧
def update_settings_list():
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        settings = config.sections()
        settings_listbox.delete(0, tk.END)  # 既存のアイテムを削除
        for setting in settings:
            settings_listbox.insert(tk.END, setting)
    except Exception as e:
        messagebox.showerror("エラー", "設定の読み込み中にエラーが発生しました:\n" + str(e))

# 設定ファイルからMacアドレスとブロードキャストアドレスを読み込む
def load_settings(setting_name):
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        broadcast_ip_entry.delete(0, tk.END)
        target_mac_entry.delete(0, tk.END)
        if config.has_section(setting_name):
            if config.has_option(setting_name, "BroadcastIP"):
                broadcast_ip_entry.insert(0, config.get(setting_name, "BroadcastIP"))
            if config.has_option(setting_name, "TargetMAC"):
                target_mac_entry.insert(0, config.get(setting_name, "TargetMAC"))
        setting_name_entry.delete(0, tk.END)  # 読み込んだ設定名をクリア
        setting_name_entry.insert(0, setting_name)  # 読み込んだ設定名を表示
    except Exception as e:
        messagebox.showerror("エラー", "設定の読み込み中にエラーが発生しました:\n" + str(e))

# 設定ファイルにMacアドレスとブロードキャストアドレスを保存
def save_settings(setting_name):
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        if not config.has_section(setting_name):
            config.add_section(setting_name)
        config.set(setting_name, "BroadcastIP", broadcast_ip_entry.get())
        config.set(setting_name, "TargetMAC", target_mac_entry.get())
        with open(config_file, "w") as configfile:
            config.write(configfile)
        messagebox.showinfo("通知", "設定を保存しました.")
        update_settings_list()  # 保存後にリストを更新
    except Exception as e:
        messagebox.showerror("エラー", "設定の保存中にエラーが発生しました:\n" + str(e))

# マジックパケットを送信する関数
def send_magic_packet():
    broadcast_ip = broadcast_ip_entry.get()
    target_mac = target_mac_entry.get()

    if not broadcast_ip or not target_mac:
        messagebox.showerror("エラー", "ブロードキャストIPアドレスと対象のMACアドレスを入力してください.")
        return

    # マジックパケットを構築
    mac_bytes = binascii.unhexlify(target_mac.replace(":", ""))
    magic_packet = b'\xFF' * 6 + mac_bytes * 16

    # ソケットを作成してマジックパケットを送信
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (broadcast_ip, 9))
        sock.close()
        messagebox.showinfo("通知", "マジックパケットを送信しました.")
    except Exception as e:
        messagebox.showerror("エラー", "マジックパケットの送信中にエラーが発生しました:\n" + str(e))

# 設定一覧から選択された設定を読み込む関数
def load_selected_setting():
    selected_setting = settings_listbox.get(settings_listbox.curselection())
    load_settings(selected_setting)

# メインウィンドウを作成
app = tk.Tk()
app.title("マジックパケット送信アプリ")
app.geometry("400x400")

# 設定名の入力フィールド
setting_name_label = tk.Label(app, text="設定名:")
setting_name_label.pack()
setting_name_entry = tk.Entry(app)
setting_name_entry.pack()

# ブロードキャストIPアドレスの入力フィールド
broadcast_ip_label = tk.Label(app, text="ブロードキャストIPアドレス:")
broadcast_ip_label.pack()
broadcast_ip_entry = tk.Entry(app)
broadcast_ip_entry.pack()

# 対象のMACアドレスの入力フィールド
target_mac_label = tk.Label(app, text="対象のMACアドレス:")
target_mac_label.pack()
target_mac_entry = tk.Entry(app)
target_mac_entry.pack()

# マジックパケット送信ボタン
send_button = tk.Button(app, text="マジックパケットを送信", command=send_magic_packet)
send_button.pack()

# 保存された設定一覧のリストボックス
settings_listbox = tk.Listbox(app)
settings_listbox.pack()

# 設定一覧の初期表示
update_settings_list()

# 宛先を追加するボタン
def add_destination():
    setting_name = setting_name_entry.get()
    if not setting_name:
        messagebox.showerror("エラー", "設定名を入力してください.")
        return
    save_settings(setting_name)

add_button = tk.Button(app, text="宛先を追加", command=add_destination)
add_button.pack()


# 設定一覧から選択された設定を読み込む関数
def load_selected_setting():
    selected_indices = settings_listbox.curselection()
    if not selected_indices:
        messagebox.showerror("エラー", "設定を選択してください。")
        return
    selected_setting = settings_listbox.get(selected_indices[0])  # 最初の選択を使用
    load_settings(selected_setting)

# 設定読み込みボタン
load_selected_setting_button = tk.Button(app, text="選択した設定を読み込む", command=load_selected_setting)
load_selected_setting_button.pack()

# 宛先を削除する関数
def delete_selected_setting():
    selected_indices = settings_listbox.curselection()
    if not selected_indices:
        messagebox.showerror("エラー", "削除する設定を選択してください。")
        return
    selected_setting = settings_listbox.get(selected_indices[0])
    
    # 設定ファイルから削除
    config = configparser.ConfigParser()
    config.read(config_file)
    if config.has_section(selected_setting):
        config.remove_section(selected_setting)
        with open(config_file, "w") as configfile:
            config.write(configfile)
    
    update_settings_list()  # リストを更新

# 削除ボタンを作成
delete_button = tk.Button(app, text="選択した宛先を削除", command=delete_selected_setting)
delete_button.pack()


# ウィンドウを表示
app.mainloop()
