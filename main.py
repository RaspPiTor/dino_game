from tkinter import messagebox
import tkinter.ttk as ttk
import tkinter as tk
import random
import threading
import queue
import time


class ThreadedManager(threading.Thread):
    def __init__(self, q_input, q_display, size=100):
        threading.Thread.__init__(self)
        self.q_input = q_input
        self.q_display = q_display
        self.size = size
    def run(self):
        start = time.time()
        ideal_loop_duration = .2
        player = [round(self.size/2), 0]
        objects = []
        last_jumped = 0
        jump_duration = 1
        last_loop = 0
        while True:
            time.sleep(0.01)
            try:
                command = self.q_input.get(0)
            except queue.Empty:
                command = []
            if command:
                if command == 'reset':
                    player = [round(self.size/2), 0]
                    objects = []
                elif command == 'j':
                    if round(time.time() - last_jumped, 2) > jump_duration:
                        last_jumped = time.time()
                        player[1] = 1
            if time.time() - last_loop >= ideal_loop_duration:
                last_loop = time.time()
                ideal_loop_duration *= .999
                if player[1] and time.time() - last_jumped > jump_duration:
                    player[1] = 0
                if len(objects) < random.randint(0, 6) and random.randint(0, 5) == 0:
                    objects.append([self.size -1, 0])
                for o in objects: 
                    o[0] -= 1
                while objects and objects[0][0] <= 0:
                    del objects[0]
                for o in objects:
                    if o == player:
                        messagebox.Message(message='You lost with time: %s' % (time.time() - start)).show()
                        player = [round(self.size/2), 0]
                        objects = []
                        ideal_loop_duration = .2
                        start = time.time()

            
            self.q_display.put(('d', player, objects, time.time() - start, ideal_loop_duration))

class GUI(ttk.Frame):
    def __init__(self, master=None, size=50):
        ttk.Frame.__init__(self)
        ttk.Label(self, text='Time:').grid(row=0, column=0)
        self.time = ttk.Label(self, text='0')
        self.time.grid(row=0, column=1)
        ttk.Label(self, text='Ideal Loop duration:').grid(row=0, column=2)
        self.loop_duration = ttk.Label(self, text='0')
        self.loop_duration.grid(row=0, column=3)
        self.main_board = ttk.Frame(self)
        self.main_board.grid(row=1, columnspan=100)
        self.size = size
        self.board = []
        for row in range(5):
            new_row = []
            for column in range(size):
                new_row.append(ttk.Label(self.main_board, text=' '))
                new_row[-1].grid(row=row, column=column, columnspan=2)
            self.board.append(new_row)
        self.board.reverse()
        for column in range(column):
            ttk.Label(self.main_board, text='~').grid(row=5, column=column)
        self.q_input = queue.Queue()
        self.q_display = queue.Queue()
        ThreadedManager(self.q_input, self.q_display, size).start()
        self.bind_all('<space>', self.space_bar)
        self.to_wipe = []
        self.refresh_everything()
    def refresh_everything(self):
        for column, row in self.to_wipe:
            self.board[row][column]['text'] = ' '
            self.board[row][column+1]['text'] = ' '
            self.board[row][column-1]['text'] = ' '
            self.board[row - 1][column]['text'] = ' '
        self.to_wipe.clear()
        command = ['']
        try:
            while True:
                command = self.q_display.get(0)
        except queue.Empty:
            if command[0] == 'd':
                self.board[command[1][1]][command[1][0]]['text'] = '&'
                self.board[command[1][1]+1][command[1][0]]['text'] = '&'
                self.to_wipe.append(command[1])
                self.to_wipe.append((command[1][0], command[1][1]+1))
                for o in command[2]:
                    self.board[o[1]][o[0]]['text'] = 'o'
                    self.to_wipe.append(o)
                self.time['text'] = str(command[3])[:10]
                self.loop_duration['text'] = str(command[4])[:10]
        self.after(10, self.refresh_everything)
    def space_bar(self, event):
        self.q_input.put('j')
gui = GUI()
gui.grid()
gui.mainloop()
