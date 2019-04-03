from tkinter import *  # python 3
from tkinter import font  as tkfont  #
from random import *
import sys, socket, threading, time
from datetime import datetime
from Client import *

class SampleApp(Tk):
    def __init__(self,*args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.resizable(width=False, height=False)
        self.title("Le jeu du ROBOT")
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = Frame(self)
        container.pack(side=TOP, fill="both", expand=YES)

        self.frames = {}
        for F in (StartPage, PageOne):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.config(width=100, height=100, bg="#41B77F")
        frame.tkraise()

class StartPage(Frame):

    def __init__(self,parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.pack(fill=BOTH)

        label = Label(self, text="Bienvenue sur le jeu du ROBOT :)", font=("Courrier", 40), bg='#41B77F', fg='white')
        label.pack(side="top", fill=X, pady=80)

        button1 = Button(self, text="JOUER", font=("Courrier", 25), bg='white', fg='#01D176',
                         command=lambda: controller.show_frame("PageOne"))
        button2 = Button(self, text="QUITTER", font=("Courrier", 25), bg='white', fg='#01D176', command=self.quit)
        button1.pack(pady=25, padx=150, fill=X)
        button2.pack(pady=15, padx=150, fill=X)

class PageOne(Frame):

    def __init__(self,parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.label_title = Label(self, text="Entrez un pseudo", font=("Courrier", 40), bg='#41B77F', fg='white')
        self.label_title.pack(pady=50)

        self.text = StringVar()
        self.entry_subtitle = Entry(self, textvariable=self.text, font=("Courrier", 40), bg='#01D176', fg='white')
        self.entry_subtitle.pack(pady=10, padx=100, fill=X)

        #self.text = Text(self)
        #self.text.pack(pady=10, padx=100, fill=X)
        
        self.button_jouer = Button(self, text="Jouer", font=("Courrier", 25), bg='white', fg='#01D176',
                                   command=self.connexion)
        self.button_jouer.pack(pady=10, padx=100, fill=X)

        self.button_retour = Button(self, text="Retour", font=("Courrier", 25), bg='white', fg='#01D176',
                                    command=lambda: controller.show_frame("StartPage"))
        self.button_retour.pack(pady=10, padx=100, fill=X)

    def connexion(self):
        #print(self.text.get())
        name = self.text.get()
        connecter(name)
        app = PageTwo()
        app.mainloop()

class PageTwo(Tk):
    def createWidgets(self):
        # Veleur
        self.value_etat_pause = IntVar()
        self.value_etat_start = IntVar()
        self.value_mode_alea = IntVar()
        self.value_mode_manu = IntVar()

        self.menuBar = Menu(master=self)

        self.menu_robot = Menu(self.menuBar, tearoff=1)

        # etat menu
        self.submenu_robot_etat = Menu(self.menuBar, tearoff=0)
        self.submenu_robot_etat.add_command(label="Pause",activebackground="#FE0F00", command=self.pause)
        self.submenu_robot_etat.add_command(label="Marche",activebackground="#02C380", command=self.start)

        # mode menu
        self.submenu_robot = Menu(self.menuBar, tearoff=0)
        self.submenu_robot.add_command(label="Automatique", activebackground="#02C380",  command=self.automatique)
        self.submenu_robot.add_command(label="Manuelle", activebackground="#02C380", command=self.manuelle)

        self.menu_robot.add_command(label="Créer un robot", command=self.placer_robot, activebackground="#FE8300")
        self.menu_robot.add_cascade(label="Etat", menu=self.submenu_robot_etat, activebackground="#FE8300")
        self.menu_robot.add_cascade(label="Mode", menu=self.submenu_robot, activebackground="#FE8300")
        self.menu_robot.add_command(label="Quitter", command=self.quit, activebackground="#FE0F00")

        self.menuBar.add_cascade(label="Robot", menu=self.menu_robot)

        self.menu2 = Menu(self.menuBar, tearoff=0)
        self.menu2.add_command(label="Changer Pseudo", command=lambda: print("hello"), activebackground="#FE8300")
        self.menu2.add_command(label="Information carte", command=lambda: print("hello"), activebackground="#FE8300")
        self.menuBar.add_cascade(label="Joueur", menu=self.menu2)

        self.menu3 = Menu(self.menuBar, tearoff=0)
        self.menu3.add_command(label="Règle du jeu", command=lambda: print("hello"), activebackground="#FE8300")
        self.menuBar.add_cascade(label="Aide", menu=self.menu3)

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.resizable(width=False, height=False)
        self.createWidgets()
        self.config(menu=self.menuBar)
        self.title("Le jeu du ROBOT")
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        width = 1050
        height = 600
        container = Frame(self)
        container.pack(side=TOP, fill="both", expand=YES)

        self.terrain = Canvas(container, width=width, height=height, bg='#EBF1D3', bd=0)
        self.terrain.pack(fill=X)

        self.carreau = [
            [self.terrain.create_rectangle(i * 30, j * 30, (i + 1) * 30, (j + 1) * 30, fill="#EBF1D3") for i in
             range(35)]
            for j in range(20)]

        self.couleurs = ['#677E52', '#B9121B', '#E70739', '#F0F168', '#8FCF3C',
                         '#34396E', '#FF5B2A', '#6E81BD', '#E0DC63', '#252545']

        self.couleurs_robot = ['#878787']

        #self.terrain.bind('<ButtonRelease>', self.clic)
        #label coord carreau
        #self.Coord = Label(container)
        #self.Coord.pack(pady='10px', side=LEFT)



        self.pause = Label(container)
        self.pause.pack(pady='5px')

        self.manu = Label(container)
        self.manu.pack(pady='5px')

        self.terrain.bind_all('<Key>', self.deplacer_robot)
    def test(self):
        print("hello")

    def placer_robot(self):
        global robot
        i = 9
        j = 17
        robot = self.terrain.create_rectangle(j * 30, i * 30, j * 30 + 30, i * 30 + 30, fill='#AEAEAE')
        self.terrain.itemconfigure(self.carreau[i][j], fill=robot)

    def deplacer_robot(self, event):
        key = event.keysym
        if key == "Right":
            self.terrain.move(robot, 30, 0)
        elif key == "Left":
            self.terrain.move(robot, -30, 0)
        elif key == "Up":
            self.terrain.move(robot, 0, -30)
        elif key == "Down":
            self.terrain.move(robot, 0, 30)

    def aleatoire(self):
        # cette fonction change les couleurs des carreaux aléatoirement
        # sans intervention humaine
        i = randint(0, 9)
        j = randint(0, 9)
        self.terrain.itemconfigure(self.carreau[i][j], fill=choice(self.couleurs))
        self.terrain.after(40, self.aleatoire)

    def clic(self, event):
        j = event.x // 30
        i = event.y // 30
        self.Coord['text'] = 'Les coordonnées du carreau cliqué sont (' + str(i) + ',' + str(j) + ')'

    def pause(self):
        global pause
        pause = True
        if pause:
            self.pause['text'] = "ETAT : Pause"
            self.terrain.unbind_all('<Key>')

    def start(self):
        pause = False
        if not pause:
            self.pause['text'] = ""
            self.terrain.bind_all('<Key>', self.deplacer_robot)

    def manuelle(self):
        global manu
        manu = True
        if manu:
            self.manu['text'] = "MODE : Manuelle"

    def automatique(self):
        manu = False
        if not manu:
            self.manu['text'] = "MODE : Automatique"
            self.terrain.unbind_all('<Key>')

#class Client(PageOne):
 #   def __init__(self):
  #      self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   #     sock.connect(("localhost", 8001))
    #   PageOne.__init__(self, *args, **kwargs):


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
