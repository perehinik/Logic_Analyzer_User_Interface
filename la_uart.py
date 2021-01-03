# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 18:56:48 2020
@author: Ivan Perehiniak
@project: Logic Analiser
"""
from __future__ import print_function
from tkinter import *
from tkinter.ttk import Checkbutton,Combobox
from tkinter import (Tk,Frame,Label,Button,Scale,HORIZONTAL, 
                    StringVar,Entry,IntVar,Toplevel)

class uart(Frame) :
    def __init__(self,master):
        self.master = master
        self.dataPin = 0
        self.baudRate = 9600
        self.parity = 0
        
        self.PusleWidth = 1.0
        
        self.decode_index  = []
        self.decode_state1 = []
        self.decode_state2 = []
        self.decode_position = []
        self.decode_text     = []
        
    def set_decode(self,channelStates):
        #self.master.withdraw()
        self.top = Toplevel(self.master)
        self.top.geometry("300x160")
        self.top.title("uart") 
        self.top.grab_set()
        
        self.datalab = Label(self.top, text="data pin:")
        self.datalab.place(x = 80,y = 20)
        
        self.baudlab = Label(self.top, text="baud rate:")
        self.baudlab.place(x = 80,y = 50)
        
        self.dataCombo = Combobox(self.top, state="readonly",width = 8)
        self.dataCombo.place(x = 140,y = 20)
        #self.SdaCombo.current(0)
        
        self.BaudVar = StringVar()
        self.BaudVar.set(str(self.baudRate))
        self.BaudEntry = Entry(self.top, width=11,textvariable = self.BaudVar)
        self.BaudEntry.place(x = 140,y = 50)
        
        data_in_temp = 100
        for i in range(0,len(channelStates)):
            if(channelStates[i] == 1 and i == self.dataPin):
                data_in_temp = i
                
        for i in range(0,len(channelStates)):
            if(channelStates[i] == 1 and data_in_temp == 100):
                data_in_temp = i

        if (data_in_temp == 100):
            data_in_temp = 0
        
        self.dataPin = data_in_temp
        
        self.dataCombo['values'] += (str(self.dataPin))
        for i in range(0,len(channelStates)):
            if (channelStates[i] == 1):
                if str(i) not in self.dataCombo['values']:
                    self.dataCombo['values'] += (str(i),)
        
        self.parity_var = IntVar()
        self.CB1 = Checkbutton(self.top, 
                               text='Parity bit',
                               variable=self.parity_var, 
                               onvalue=1, 
                               offvalue=0) #
        self.CB1.place(x = 140,y = 80)
        self.parity_var.set(self.parity)        
        
        self.Button = Button(self.top, 
                             text = "OK",
                             height=2, 
                             width=18, 
                             command = self.OkCallBack)
        self.Button.place(x = 80,y = 110)
        self.dataCombo.current(0)
        
        self.top.protocol('WM_DELETE_WINDOW', self.exit_handler)
        self.top.mainloop()
    
    def decode(self,results,max_index,frq):
        self.decode_index =  []
        self.decode_state1 =  []
        self.decode_state2 =  []
        self.decode_position = []
        self.decode_text = []
        self.decode_index.append(0)
        self.decode_state1.append(1)
        self.decode_state2.append(0)
        
        self.bit_count = 0
        self.data = 0
        self.decodeStrTmp = ""
        
        self.PulseWidth = frq / self.baudRate
        
        i = 0
        while i < max_index:
            if (results[self.dataPin][i-1]==1 and results[self.dataPin][i]==0):#START
                offsetStart = int(round(self.PulseWidth))
                offset8 = int(round(self.PulseWidth * 8 + self.PulseWidth/2))  
                
                
                self.add_point(i)
                self.decode_position.append(i+(self.PulseWidth/5))
                self.decode_text.append("St")
                
                offsetDecode = (offset8 - offsetStart)//2
                
                self.data = 0
                for d in range(0,8):
                    self.data = self.data>>1
                    offset = int(round(self.PulseWidth * (d+1) + self.PulseWidth/2))
                    self.data += results[self.dataPin][i+offset] * 128
                
                self.add_point(i+offsetStart)
                self.decode_position.append(i+offsetDecode)
                self.decode_text.append(str(hex(self.data)))
                
                if(self.parity == 0):
                    offsetStop = int(round(self.PulseWidth * 9))
                    self.add_point(i+offsetStop)
                    self.decode_position.append(i+offsetStop+ (self.PulseWidth/5))
                    self.decode_text.append("Sp")
                else:
                    offsetParity = int(round(self.PulseWidth * 9))
                    offsetStop = int(round(self.PulseWidth * 10))
                    self.add_point(i+offsetParity)
                    self.decode_position.append(i+offsetParity+ (self.PulseWidth/5))
                    self.decode_text.append(str(results[self.dataPin][i+int(offsetParity + self.PulseWidth/2)]))
                    
                    self.add_point(i+offsetStop)
                    self.decode_position.append(i+ offsetStop + (self.PulseWidth/5))
                    self.decode_text.append("Sp")
                
                i+=offsetStop
                i+=1
            else:
                i+=1
    def OkCallBack(self):
        self.dataPin = int(self.dataCombo.get())
        self.baudRate = int(self.BaudVar.get())
        self.exit_handler()
        self.parity = self.parity_var.get()
    
    def exit_handler(self):
        self.top.grab_release()
        self.top.destroy()
    def add_point(self,i):
        self.decode_index.append(i)
        self.decode_state1.append(self.decode_state1[-1])
        self.decode_state2.append(self.decode_state2[-1])
        self.decode_index.append(i+0.5)
        self.decode_state1.append(1-self.decode_state1[-1])
        self.decode_state2.append(1-self.decode_state2[-1])

if __name__ == "__main__":
    root = Tk()   
    root.title("Root Window")   
    root.geometry("450x300") 
    app = uart(root)
    app.set_decode([1,1,1,1,1,1,1,1])
    