BACKGROUND_COLOR = "#B1DDC6"

import os
from tkinter import *
from tkinter import messagebox

import random

import pandas as pd
import pyperclip


# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Flashy")
window.config(padx=50, pady=50,bg=BACKGROUND_COLOR)
# window.config(width=900, height=626)
canvas = Canvas(height=526, width=800)
front_img = PhotoImage(file="images/card_front.png")
back_img = PhotoImage(file="images/card_back.png")
canvas_image = canvas.create_image(400, 263, image=front_img)
title = canvas.create_text(400,150,text="Title",font=("Ariel",40,"italic"))
word = canvas.create_text(400,263,text="Word",font=("Ariel",40,"bold"))
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=1, column=0,columnspan = 2)

def flip_card():
    canvas.itemconfig(canvas_image, image=back_img)
    canvas.itemconfig(word, text=slovak, fill="white")
    canvas.itemconfig(title, text="Slovensky", fill="white")

german = ""
slovak = ""

def get_word():
    global german
    global slovak
    global flip_timer
    global nested_dict
    rebuild_nested_dict()
    window.after_cancel(flip_timer)
    if level() == "all" or level() == "Vyber si uroven":
        # chosen_level = random.randint(1, 5)
	    chosen_level = 1
    else:
        chosen_level = int(level())

    count = len(nested_dict[chosen_level])
    print(f"Count of dict: {count}")
    random_item = random.randint(0, count - 1)
    print(f"random_item = {random_item}")
    print(f"Level: {chosen_level}")
    print(nested_dict[chosen_level][random_item])
    new_word_german = nested_dict[chosen_level][random_item]["german"]
    new_word_slovak = nested_dict[chosen_level][random_item]["slovak"]
    canvas.itemconfig(word, text=new_word_german,fill="black")
    canvas.itemconfig(title, text="Deutsch",fill="black")
    canvas.itemconfig(canvas_image, image=front_img)
    german = new_word_german
    slovak = new_word_slovak
    flip_timer = window.after(10000, flip_card)

selected_level = StringVar()
selected_level.set("Vyber si uroven")  # Default value

# List of options
options = ["1", "2", "3", "4","5","6","7","8","9","all"]

dropdown = OptionMenu(window, selected_level, *options)
dropdown.config(font=("Ariel",20,"bold"))
dropdown.grid(row=0,column=0,columnspan=2)


# ---------------------------- New flash Card ------------------------------- #
df = pd.read_csv("data/german_slovak.csv")

if not os.path.exists("data/words_to_learn.csv"):
    df.to_csv("data/words_to_learn.csv",index=False)

df2 = pd.read_csv("data/words_to_learn.csv")

def remove_word():
    global df2
    global german
    print(f"removed word: {german}")
    df2 = df2[df2['german'] != german]
    df2.to_csv('data/words_to_learn.csv', index=False)
    get_word()

def rebuild_nested_dict():
    global nested_dict, df2
    df2 = pd.read_csv("data/words_to_learn.csv")
    nested_dict = {}

    for german, slovak in df2.groupby('level'):
        nested_dict[german] = slovak.drop(columns='level').to_dict(orient='records')


##Buttons
right_image = PhotoImage(file="images/right.png")
right_button = Button(image=right_image, highlightthickness=0,command=remove_word)
right_button.grid(row=2, column=1)

wrong_image = PhotoImage(file="images/wrong.png")
wrong_button = Button(image=wrong_image, highlightthickness=0,command=get_word)
wrong_button.grid(row=2, column=0)

nested_dict = {}

for german, slovak in df2.groupby('level'):
    nested_dict[german] = slovak.drop(columns='level').to_dict(orient='records')

def level():
    return selected_level.get()

flip_timer = window.after(3000, flip_card)

get_word()

print(german)
print(slovak)


window.mainloop()

