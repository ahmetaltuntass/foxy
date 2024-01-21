import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO
import customtkinter
import time
import pyaudio
import wave
import os
import webbrowser
import re


GENIUS_API_KEY = 'WExZFbF3aLHJt1ncFhU9usEckelpYPcmyEfKvrdp6lEWGMBwZMm-kCmpkLboxUkq'
max_results = 3

main_path= os.path.dirname(os.path.realpath(__file__))
images_path = os.path.join(main_path,"images")

search_image_path = os.path.join(images_path, "searchbut.png")
list_image_path = os.path.join(images_path, "list.png")
nw_button_path = os.path.join(images_path, "listen.png")
switch_image_path = os.path.join(images_path, "switch.png")
foxy_image_path = os.path.join(images_path, "foxy.png")

splash_image_path = os.path.join(images_path, "foxysplash.png")
c1_image_path = os.path.join(images_path, "c1.png")
c2_image_path = os.path.join(images_path, "c2.png")


def record_audio(file_name, seconds):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    print("Recording...")

    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wave_file = wave.open(file_name, 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()

def recognize_song(audio_file_path):
    global songinfo  # songinfo'yu global olarak tanımla

    url = "https://api.audd.io/"
    api_token = "9636c6afe9b689603c39ddd0ab3fd159"  

    files = {'file': open(audio_file_path, 'rb')}
    data = {'api_token': api_token}

    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        print("Song recognized:")
        print(response.json())
        song_data = response.json().get('result')  # Use get method to handle missing 'result' key

        if song_data is None:
            print('Could not find')
            show_couldnt_find_label()
            


        else:
            try:
                artist_name = song_data['artist']
                song_name = song_data['title']
                songinfo = (song_name +' '+ artist_name)
                print(songinfo)
                search_lyrics_button_click2()
            except KeyError as e:
                print(f"Error: {e} not found in song_data")
                
    else:
        print("Recognition failed")

def show_couldnt_find_label():
    
    couldntfind_label = tk.Label(app, text='Could not Recognize', font=('JetBrains Mono', 30),background="#242424",fg='white')
    couldntfind_label.place(relx=0.45, rely=0.45)
    app.after(3000, lambda: destroy_label(couldntfind_label))

def destroy_label(label):
    label.destroy()
    
def record_and_recognize():
    file_name = "recorded_audio.wav"  
    record_audio(file_name, seconds=7)
    recognize_song(file_name)

def search_songs_by_lyrics(lyrics, max_results):
    base_url = 'https://api.genius.com'
    search_endpoint = '/search'
    headers = {
        'Authorization': f'Bearer {GENIUS_API_KEY}',
    }
    params = {
        'q': lyrics,
    }

    try:
        response = requests.get(base_url + search_endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        
        results = []
        album_cover_urls = []

        for hit in data['response']['hits'][:max_results]:
            song_info = hit['result']

            song_title = song_info['title']
            song_artist = song_info['primary_artist']['name']
            song_url = song_info['url']
            album_cover_url = song_info['song_art_image_url']
            album_cover_urls.append(album_cover_url)

            result = f"{song_title} by {song_artist}\nGenius Lyrics URL: {song_url}"
            results.append(result)

        return results, album_cover_urls

    except requests.exceptions.RequestException as e:
        error_message = f"An error occurred: {e}"
        messagebox.showerror("Error", error_message)
        return [], []

def search_lyrics_button_click2():
    global songinfo, album_cover_frame  # songinfo ve album_cover_frame'u global olarak tanımla

    # Eğer önceki album_cover_frame varsa, yok et
    if album_cover_frame:
        album_cover_frame.destroy()

    lyrics = songinfo
    results, album_cover_urls = search_songs_by_lyrics(lyrics, 1)
    
    album_cover_frame = tk.Frame(app)

    if album_cover_urls:
        album_cover_frame.grid(row=1, column=0, padx=10, pady=10)

    for i, album_cover_url in enumerate(album_cover_urls):
        if i < max_results:
            try:
                response = requests.get(album_cover_url)
                response.raise_for_status()
                album_cover_image = Image.open(BytesIO(response.content))

                # Albüm kapağının ayarlanması
                new_width = 250
                new_height = 250
                album_cover_image = album_cover_image.resize((new_width, new_height))

                album_cover_image = ImageTk.PhotoImage(album_cover_image)

                album_cover_label = tk.Label(album_cover_frame, image=album_cover_image)
                album_cover_label.image = album_cover_image
                album_cover_label.grid(row=i, column=0, padx=5, pady=5)

                # Şarkının başlıklarının düzeni
                text = results[i]
                text_label = tk.Label(album_cover_frame, text=text, font=('Arial', 20),background="#242424",fg='white')
                text_label.grid(row=i, column=5, padx=5, pady=5)

                # Genius Lyrics URL'sini çıkarmak için regex deseni
                url_pattern = r'https://genius\.com/[^\s]+'
                matches = re.search(url_pattern, text)
                
                if matches:
                    genius_lyrics_url = matches.group()
                    goweb = tk.Label(album_cover_frame, text="Go to Website", font=('Arial', 20, 'underline'), fg="black", cursor="hand2")
                    goweb.grid(row=50, column=10, padx=5, pady=5, columnspan=10)  # Placing below the album cover
                    goweb.bind("<Button-1>", lambda event, url=genius_lyrics_url: webbrowser.open(url))
                
            except requests.exceptions.RequestException:
                messagebox.showerror("Error", "Failed to load album cover")

# Önceki album_cover_frame'i tanımla (başlangıçta herhangi bir değeri yok)
album_cover_frame = None


def search_lyrics_button_click():
    global album_cover_frame  # album_cover_frame'u global olarak tanımla

    # Eğer önceki album_cover_frame varsa, yok et
    if album_cover_frame:
        album_cover_frame.destroy()

    lyrics = lyrics_entry.get()
    results, album_cover_urls = search_songs_by_lyrics(lyrics, max_results)
    album_cover_frame = customtkinter.CTkFrame(app)

    if album_cover_urls:
        album_cover_frame.grid(row=1, column=0, padx=10, pady=10)

    for i, album_cover_url in enumerate(album_cover_urls):
        if i < max_results:
            try:
                response = requests.get(album_cover_url)
                response.raise_for_status()
                album_cover_image = Image.open(BytesIO(response.content))

                # Albüm kapağının ayarlanması
                new_width = 250
                new_height = 250
                album_cover_image = album_cover_image.resize((new_width, new_height))

                album_cover_image = ImageTk.PhotoImage(album_cover_image)

                album_cover_label = tk.Label(album_cover_frame, image=album_cover_image)
                album_cover_label.image = album_cover_image
                album_cover_label.grid(row=i, column=0, padx=5, pady=5)

                # Şarkının başlıklarının düzeni
                text = results[i]
                print(text)
                text_label = tk.Label(album_cover_frame, text=text, font=('Arial',15),background="#302c2c",fg='white')
                text_label.grid(row=i, column=5, padx=5, pady=5)
            except requests.exceptions.RequestException:
                messagebox.showerror("Error", "Failed to load album cover")


# Silme butonunun çalışması için gereken fonksiyon
def clear():
    lyrics_entry.delete(0, END)
#label kaldirma




# |||||||||||||||||||||||||||          ARAYÜZ(UI)          |||||||||||||||||||||||||||
customtkinter.set_appearance_mode("system")
app = customtkinter.CTk()
app.title("Foxy - Your Special Song Finder")
app.geometry("1920x1080")

search_image = ImageTk.PhotoImage(Image.open(search_image_path).resize((40,40),))
list_image = ImageTk.PhotoImage(Image.open(list_image_path).resize((40,40),))

button = customtkinter.CTkButton(master=app, image=search_image ,text="Search",command=search_lyrics_button_click,
                                 font=("JetBrains Mono",24),
                                 text_color="black",
                                 fg_color="white",
                                 width=64,
                                 height=40,
                                 hover_color="orange",
                                 corner_radius=20,
                                 compound="left")
button.place(relx=0.755,rely=0.05, anchor = tk.CENTER)

def open_foxy():
    record_and_recognize()




nw_button = ImageTk.PhotoImage(Image.open(nw_button_path).resize((80, 80)))
switch_image = ImageTk.PhotoImage(Image.open(switch_image_path).resize((40, 40)))

switch_button = customtkinter.CTkButton(
    master=app,
    text="Foxy!",
    image=nw_button,
    font=("JetBrains Mono", 20),
    text_color="black",
    fg_color="white",
    hover_color="orange",
    corner_radius=20,
    compound="left",
    command=open_foxy
)
switch_button.place(relx=0.91, rely=0.05, anchor=tk.CENTER)


lyrics_entry = customtkinter.CTkEntry(master=app,placeholder_text="Enter your keywords",
                                      height=70,
                                      width=500,
                                      corner_radius=20,
                                      font=("Work Sans",16))   
                                    
                                    
lyrics_entry.place(relx=0.53, rely=0.043, anchor=tk.CENTER)

clear_button = customtkinter.CTkButton(master=app,text="X",command= clear,font=("Work Sans",20),
                                       height=2,
                                       width=2,
                                       text_color="gray",
                                       bg_color="#343638",
                                       fg_color="#343638",
                                       hover_color="red",
                                       )
clear_button.place(relx=0.67, rely=0.02)



#Sol üst logo
my_label = customtkinter.CTkLabel(app, text=" ")
my_label.grid(pady=20)

image = Image.open(foxy_image_path)

new_width = 200 #645
new_height = 100 #81
resized_image = image.resize((new_width, new_height))

photo = ImageTk.PhotoImage(resized_image)
label = tk.Label(master=app, image=photo, background="#242424")
label.image = photo
label.grid(row=0, column=0, sticky="nw", padx=10, pady=10)  # padx ve pady ekledim



#|||||||||||||||||||||||||||          SPLASHSCREEN         |||||||||||||||||||||||||||

def new_win():
    app.mainloop()

def display_splash():
    splash = tk.Toplevel()
    width_of_window = 1420
    height_of_window = 768
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (width_of_window / 2)
    y_coordinate = (screen_height / 2) - (height_of_window / 2)
    splash.geometry("%dx%d+%d+%d" % (width_of_window, height_of_window, x_coordinate, y_coordinate))
    splash.overrideredirect(1)


    splash_image = Image.open(splash_image_path)
    splash_image = splash_image.resize((200,200))
    photo = ImageTk.PhotoImage(splash_image)



    for i in range(3):
        Frame(splash, width=1920, height=1080, bg='#272727').place(x=500,y=95)
        label1=Label(splash, text='FOXY', fg='white', bg='#272727') 
        label1.configure(font=("JetBrains Mono", 100, "bold"))   
        label1.place(x=830,y=200)
        label1=Label(splash, text='Your Personal Song Finder', fg='white', bg='#272727') 
        label1.configure(font=("JetBrains Mono Thin", 20, "bold"))
        label1.place(x=835,y=340)
        label1=Label(splash, text='V2023.12', fg='white', bg='#272727') 
        label1.configure(font=("JetBrains Mono ", 20, "bold"))
        label1.place(x=1130,y=375)
        label1 = tk.Label(splash, text='Loading...', fg='white', bg='#272727')
        label1.configure(font=("Work Sans", 20,"bold"))
        label1.place(x=900, y=600)
        image_label = tk.Label(splash,image=photo,bg="#272727")
        image_label.splash_image = photo
        image_label.place(x=600,y=170)
       


        
        splash.update_idletasks()
        time.sleep(0.5)
    
       



        image_a = ImageTk.PhotoImage(Image.open(c2_image_path))
        image_b = ImageTk.PhotoImage(Image.open(c1_image_path))
        


        for i in range(3):
            l1 = Label(splash,image=image_a,border=0,relief=SUNKEN).place(x=930,y=700)
            l2 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=950,y=700)
            l3 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=970,y=700)
            l4 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=990,y=700)
            splash.update_idletasks()
            time.sleep(0.5)
            
            l1 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=930,y=700)
            l2 = Label(splash,image=image_a,border=0,relief=SUNKEN).place(x=950,y=700)
            l3 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=970,y=700)
            l4 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=990,y=700)
            splash.update_idletasks()
            time.sleep(0.5)

            l1 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=930,y=700)
            l2 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=950,y=700)
            l3 = Label(splash,image=image_a,border=0,relief=SUNKEN).place(x=970,y=700)
            l4 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=990,y=700)
            splash.update_idletasks()
            time.sleep(0.5)

            l1 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=930,y=700)
            l2 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=950,y=700)
            l3 = Label(splash,image=image_b,border=0,relief=SUNKEN).place(x=970,y=700)
            l4 = Label(splash,image=image_a,border=0,relief=SUNKEN).place(x=990,y=700)
            splash.update_idletasks()
            time.sleep(0.5)

        

            splash.destroy()
            new_win()






display_splash()

album_cover_frame = customtkinter.CTkFrame(app)

app.mainloop()