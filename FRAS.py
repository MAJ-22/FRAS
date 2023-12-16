import os.path
import datetime
import pickle
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import ThemedTk
import cv2
from PIL import Image, ImageTk
import face_recognition
import subprocess

def get_button(window, text, color, command, fg='white'):
    button = tk.Button(
        window,
        text=text,
        activebackground="black",
        activeforeground="white",
        fg=fg,
        bg=color,
        command=command,
        height=2,
        width=20,
        font=('Helvetica bold', 20)
    )

    return button


def get_img_label(window):
    label = tk.Label(window)
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text):
    label = tk.Label(window, text=text)
    label.config(font=("sans-serif", 21), justify="left")
    return label


def get_entry_text(window):
    inputtxt = tk.Text(window,
                       height=2,
                       width=15, font=("Arial", 32))
    return inputtxt


def msg_box(title, description):
    messagebox.showinfo(title, description)


def recognize(img, db_path):
    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found'
    else:
        embeddings_unknown = embeddings_unknown[0]

    db_dir = sorted(os.listdir(db_path))

    match = False
    j = 0
    while not match and j < len(db_dir):
        path_ = os.path.join(db_path, db_dir[j])

        file = open(path_, 'rb')
        embeddings = pickle.load(file)

        match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
        j += 1

    if match:
        return db_dir[j - 1][:-7]
    else:
        return 'unknown_person'


class App:
    def __init__(self):
        self.most_recent_capture_arr = None
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+250+100")
        self.main_window.title("FRAS")

        self.login_button_main_window = get_button(self.main_window, 'Login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=100)

        self.register_new_user_button_main_window = get_button(self.main_window, 'Register', 'gray',
                                                               self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=200)

        self.file_menu_button = get_button(self.main_window, 'Files', 'gray', self.browseFiles, fg='black')
        self.file_menu_button.place(x=750, y=300)

        self.webcam_label = get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_file = './Log_files'
        if not os.path.exists(self.log_file):
            os.mkdir(self.log_file)

        self.sub = selected_subject_value
        self.time = datetime.date.today()

        self.log_path = './Log_files/{}_{}.csv'.format(self.time, self.sub)

        with open(self.log_path, 'a') as f:
            f.write('{},{}\n'.format(selected_faculty_value, selected_subject_value))
            f.close()

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c")

        embeddings = face_recognition.face_encodings(self.register_new_user_capture)[0]

        file = open(os.path.join(self.db_dir, '{}.pickle'.format(name)), 'wb')
        pickle.dump(embeddings, file)

        msg_box('Success!', 'User was registered successfully !')

        self.register_new_user_window.destroy()
    def login(self):

            name = recognize(self.most_recent_capture_arr, self.db_dir)

            if name in ['unknown_person', 'no_persons_found']:
                msg_box('Ups...', 'Unknown user. Please register new user or try again.')
            else:
                msg_box('Welcome back !', 'Welcome, {}.'.format(name))
                with open(self.log_path, 'a') as f:
                    f.write('{},{},in\n'.format(name, datetime.datetime.now()))
                    f.close()

    def browseFiles(self):
        self.directory_path = os.path.join(os.getcwd(), 'Log_files')
        subprocess.Popen(['explorer', self.directory_path], shell=True)

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+250+100")
        self.main_window.title("FRAS")

        self.accept_button_register_new_user_window = get_button(self.register_new_user_window, 'Accept', 'green',
                                                                 self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = get_button(self.register_new_user_window, 'Try again', 'red',
                                                                    self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = get_text_label(self.register_new_user_window, 'Input name:')
        self.text_label_register_new_user.place(x=750, y=90)




options = ["", "DS", "JAVA", "DSGT", "CG", "EM-3", "DLCA"]
optionsf = ["", "Ms.Neha Raut", "Ms.Sneha Yadav", "Ms.Bhavika Gharat", "Ms.Rujuta Vartak", "Ms.Kshitija Gharat"]

selected_subject_value = ""
selected_faculty_value = ""


def apply_theme(theme_name):
    themed_window = ThemedTk(theme=theme_name)
    themed_window.geometry("500x300+370+120")
    subject_label = ttk.Label(themed_window, text="Select Subject:")
    subject_label.pack(pady=10)
    selected_subject = tk.StringVar()
    subject_menu = ttk.OptionMenu(themed_window, selected_subject, *options)
    subject_menu.config(width=30)
    subject_menu.pack(anchor="center")  # Center alignment
    faculty_label = ttk.Label(themed_window, text="Select Faculty:")
    faculty_label.pack(pady=10)
    selected_faculty = tk.StringVar()
    faculty_menu = ttk.OptionMenu(themed_window, selected_faculty, *optionsf)
    faculty_menu.config(width=30)
    faculty_menu.pack(anchor="center")

    def update_selected_values():
        global selected_subject_value, selected_faculty_value
        selected_subject_value = selected_subject.get()
        selected_faculty_value = selected_faculty.get()

    style = ttk.Style()
    style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="black")

    def destroy_and_mainloop():
        themed_window.destroy()
        app = App()
        app.start()

    submit_button = ttk.Button(themed_window, text="Submit", command=lambda: [update_selected_values(), destroy_and_mainloop()])
    submit_button.pack(pady=20)

    themed_window.mainloop()

apply_theme("aquativo")

