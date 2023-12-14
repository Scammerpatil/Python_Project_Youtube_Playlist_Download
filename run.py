import os
from pytube import YouTube
import requests
import re
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

def foldertitle(url):
    try:
        res = requests.get(url)
    except:
        print('No internet')
        return False
    plain_text = res.text
    if 'list=' in url:
        eq = url.rfind('=') + 1
        cPL = url[eq:]
    else:
        print('Incorrect attempt.')
        return False
    return cPL

def link_snatcher(url):
    our_links = []
    try:
        res = requests.get(url)
    except:
        print('No internet')
        return False
    plain_text = res.text
    if 'list=' in url:
        eq = url.rfind('=') + 1
        cPL = url[eq:]
    else:
        print('Incorrect Playlist.')
        return False
    tmp_mat = re.compile(r'watch\?v=\S+?list=' + cPL)
    mat = re.findall(tmp_mat, plain_text)
    for m in mat:
        new_m = m.replace('&amp;', '&')
        work_m = 'https://youtube.com/' + new_m
        if work_m not in our_links:
            our_links.append(work_m)
    return our_links

def download_videos():
    url = url_var.get()
    resolution = resolution_var.get()
    folder_path = folder_path_var.get()

    if not url or not resolution or not folder_path:
        status_label.config(text='Please enter a valid URL, resolution, and folder path.')
        return

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    status_label.config(text='Downloading...')
    progress_bar["value"] = 0

    our_links = link_snatcher(url)
    os.chdir(folder_path)
    new_folder_name = foldertitle(url)

    try:
        os.mkdir(new_folder_name[:7])
    except FileExistsError:
        status_label.config(text='Folder already exists.')

    os.chdir(new_folder_name[:7])
    save_path = os.getcwd()

    for idx, link in enumerate(our_links, 1):
        try:
            yt = YouTube(link)
            main_title = yt.title
            main_title = main_title + '.mp4'
            main_title = main_title.replace('|', '')

        except:
            status_label.config(text='Connection problem. Unable to fetch video info.')
            break

        if main_title not in os.listdir(save_path):
            if resolution == '360p' or resolution == '720p':
                vid = yt.streams.filter(progressive=True, file_extension='mp4', res=resolution).first()
                status_label.config(text=f'Downloading {vid.default_filename}...')
                vid.download(save_path, on_progress_callback=update_progress)
            else:
                status_label.config(text='Invalid resolution. Please rerun the script.')
        else:
            status_label.config(text=f'Skipping "{main_title}" video.')

    status_label.config(text='Downloading finished.')
    status_label.config(text=f'All your videos are saved at {save_path}')

def update_progress(stream, chunk, remaining):
    file_size = stream.filesize
    bytes_downloaded = file_size - remaining
    progress = (bytes_downloaded / file_size) * 100
    progress_bar["value"] = progress
    root.update_idletasks()
def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_path_var.set(folder_selected)


# Tkinter GUI
root = tk.Tk()
root.title('YouTube Playlist Downloader')

# Variables
url_var = tk.StringVar()
resolution_var = tk.StringVar()
folder_path_var = tk.StringVar()

# GUI Components
url_label = tk.Label(root, text='Enter Playlist URL:')
url_entry = tk.Entry(root, textvariable=url_var, width=40)

resolution_label = tk.Label(root, text='Choose Resolution:')
resolution_combobox = ttk.Combobox(root, textvariable=resolution_var, values=['360p', '720p'])

folder_label = tk.Label(root, text='Select Folder:')
folder_entry = tk.Entry(root, textvariable=folder_path_var, width=30)
browse_button = tk.Button(root, text='Browse', command=browse_folder)

download_button = tk.Button(root, text='Download Videos', command=download_videos)
status_label = tk.Label(root, text='')

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")

# Layout
url_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
url_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')

resolution_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
resolution_combobox.grid(row=1, column=1, padx=10, pady=10, sticky='w')

folder_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
folder_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')
browse_button.grid(row=2, column=2, pady=10)

download_button.grid(row=3, column=0, columnspan=3, pady=20)
status_label.grid(row=4, column=0, columnspan=3)
progress_bar.grid(row=5, column=0, columnspan=3, pady=10)

root.mainloop()
