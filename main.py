BACKGROUND_COLOR = "#B1DDC6"

import os
from tkinter import *
from tkinter import messagebox

import random

import pandas as pd

UNIQUE_COL = "foreign"
ALL_PATH = "data/words_to_learn_all.csv"
LEARN_PATH = "data/words_to_learn.csv"
FLIP_TIME_IN_SECONDS = 5

# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Flashy")
window.config(padx=50, pady=50,bg=BACKGROUND_COLOR)
# window.config(width=900, height=626)
canvas = Canvas(height=526, width=800)
front_img = PhotoImage(file="images/card_front.png")
back_img = PhotoImage(file="images/card_back.png")
canvas_image = canvas.create_image(400, 263, image=front_img)
title = canvas.create_text(400,150,text="Title",font=("Ariel",30,"italic"))
word = canvas.create_text(400,263,text="Word",font=("Ariel",40,"bold"))
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=1, column=0,columnspan = 2)

def flip_card():
    canvas.itemconfig(canvas_image, image=back_img)
    canvas.itemconfig(word, text=translation, fill="white")
    canvas.itemconfig(title, text=f"Translation, level: {int(chosen_level)}", fill="white")

foreign = ""
translation = ""
chosen_level = ""

def get_word():
    global foreign
    global translation
    global flip_timer
    global nested_dict
    global chosen_level
    rebuild_nested_dict()
    available_levels = sorted(nested_dict.keys())
    window.after_cancel(flip_timer)
    if level() == "all" or level() == "Choose a level/all":
        chosen_level = random.choice(available_levels)
	    # chosen_level = 1
    else:
        if int(level()) not in available_levels:
            messagebox.showwarning("Warning", f"The chosen level {int(level())} does not exist in your file.\nThe app will continue with the current level.\nPlease choose an existing level from the dropdown.")
        else:    
            chosen_level = int(level())

    count = len(nested_dict[chosen_level])
    print(f"Count of dict: {count}")
    random_item = random.randint(0, count - 1)
    print(f"random_item = {random_item}")
    print(f"Level: {int(chosen_level)}")
    # print(nested_dict[chosen_level][random_item])
    new_word_foreign = nested_dict[chosen_level][random_item]["foreign"]
    new_word_translation = nested_dict[chosen_level][random_item]["translation"]
    canvas.itemconfig(word, text=new_word_foreign,fill="black")
    canvas.itemconfig(title, text=f"Foreign word, level: {int(chosen_level)}",fill="black")
    canvas.itemconfig(canvas_image, image=front_img)
    foreign = new_word_foreign
    translation = new_word_translation
    flip_timer = window.after(FLIP_TIME_IN_SECONDS*1000, flip_card)

selected_level = StringVar()
selected_level.set("Choose a level/all")  # Default value

# List of options
options = ["1", "2", "3", "4","5","all"]

dropdown = OptionMenu(window, selected_level, *options)
dropdown.config(font=("Ariel",20,"bold"))
dropdown.grid(row=0,column=0,columnspan=2)


# ---------------------------- New flash Card ------------------------------- #
df_all = pd.read_csv(ALL_PATH, sep=";")

if not os.path.exists(LEARN_PATH):
    df_all["level"] = df_all["level"].astype(int)
    df_all.to_csv(LEARN_PATH,index=False,sep=";")

df_learn = pd.read_csv(LEARN_PATH, sep=";")

def sync_to_all():
    """
    Add any missing rows (by UNIQUE_COL) from 'words_to_learn.csv' (df_learn)
    to 'words_to_learn_all.csv' (df_all). Updates both the CSV file and memory.
    Returns the number of rows added to df_all.
    """
    global df_all, df_learn

    # Identify rows in df_learn that are not yet in df_all
    missing = df_learn[~df_learn[UNIQUE_COL].isin(df_all[UNIQUE_COL])]

    if not missing.empty:
        # Append missing rows to the all-words file
        missing["level"] = missing["level"].astype(int)
        missing.to_csv(ALL_PATH, mode="a", index=False, header=False, sep=";")
        # Update df_all in memory
        df_all = pd.concat([df_all, missing], ignore_index=True)
        # Deduplicate by the unique column
        df_all = df_all.drop_duplicates(subset=[UNIQUE_COL]).reset_index(drop=True)
        # Save the cleaned result back to disk
        df_all["level"] = df_all["level"].astype(int)
        df_all.to_csv(ALL_PATH, index=False, sep=";")
        print(f"✅ Synced {len(missing)} new item(s) from words_to_learn → words_to_learn_all.")
    else:
        print("ℹ️ No new words to sync — both files are up to date.")

    return len(missing)

sync_to_all()

def remove_word():
    global df_learn
    global foreign
    print(f"removed word: {foreign}")
    df_learn = df_learn[df_learn['foreign'] != foreign]
    df_learn["level"] = df_learn["level"].astype(int)
    df_learn.to_csv(LEARN_PATH, index=False, sep=";")
    get_word()

def rebuild_nested_dict():
    global nested_dict, df_learn
    df_learn = pd.read_csv(LEARN_PATH, sep=";")
    nested_dict = {}

    for foreign, translation in df_learn.groupby('level'):
        nested_dict[foreign] = translation.drop(columns='level').to_dict(orient='records')


##Buttons
right_image = PhotoImage(file="images/right.png")
right_button = Button(image=right_image, highlightthickness=0,command=remove_word)
right_button.grid(row=2, column=1)

wrong_image = PhotoImage(file="images/wrong.png")
wrong_button = Button(image=wrong_image, highlightthickness=0,command=get_word)
wrong_button.grid(row=2, column=0)

nested_dict = {}

for foreign, translation in df_learn.groupby('level'):
    nested_dict[foreign] = translation.drop(columns='level').to_dict(orient='records')

def level():
    return selected_level.get()

flip_timer = window.after(FLIP_TIME_IN_SECONDS*1000, flip_card)

get_word()

# print(foreign)
# print(translation)


window.mainloop()

