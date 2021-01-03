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

class spi(Frame) :
    def __init__(self,master):
        self.master = master
        self.CLKIn = 0
        self.DataIn = 0
        self.SSIn = 0
        
        self.cpol = 0
        self.cpha = 0
        
        self.decode_index  = []
        self.decode_state1 = []
        self.decode_state2 = []
        self.decode_position = []
        self.decode_text     = []
        
    def set_decode(self,channelStates):
        #self.master.withdraw()
        self.top = Toplevel(self.master)
        self.top.geometry("300x210")
        self.top.title("spi") 
        self.top.grab_set()
        
        self.Datalab = Label(self.top, text="MISO/MOSI:")
        self.Datalab.place(x = 70,y = 20)
        
        self.CLKlab = Label(self.top, text="CLK:")
        self.CLKlab.place(x = 70,y = 50)
        
        self.SSlab = Label(self.top, text="SS:")
        self.SSlab.place(x = 70,y = 80)
        
        self.DataCombo = Combobox(self.top, state="readonly",width = 8)
        self.DataCombo.place(x = 150,y = 20)
        
        self.CLKCombo = Combobox(self.top, state="readonly",width = 8)
        self.CLKCombo.place(x = 150,y = 50)
        
        self.SSCombo = Combobox(self.top, state="readonly",width = 8)
        self.SSCombo.place(x = 150,y = 80)
        
        clk_in_temp = 100
        data_in_temp = 100
        ss_in_temp = 100
        
        for i in range(0,len(channelStates)):
            if(channelStates[i] == 1 and i == self.CLKIn):
                clk_in_temp = i
            if(channelStates[i] == 1 and i == self.DataIn):
                data_in_temp = i
            if(channelStates[i] == 1 and i == self.SSIn):
                ss_in_temp = i
                
        for i in range(0,len(channelStates)):
            if(channelStates[i] == 1 and clk_in_temp == 100):
                clk_in_temp = i
            if(channelStates[i] == 1 and data_in_temp == 100):
                data_in_temp = i
            if(channelStates[i] == 1 and ss_in_temp == 100):
                ss_in_temp = i
                
        
        if (clk_in_temp == 100):
            clk_in_temp = 0
        if (data_in_temp == 100):
            data_in_temp = 0
        if (ss_in_temp == 100):
            ss_in_temp = 0   
        
        self.CLKIn = clk_in_temp
        self.DataIn = data_in_temp
        self.SSIn = ss_in_temp
        
        self.DataCombo['values'] += (str(self.DataIn))
        self.CLKCombo['values'] += (str(self.CLKIn))
        self.SSCombo['values'] += (str(self.SSIn))
        for i in range(0,len(channelStates)):
            if (channelStates[i] == 1):
                if str(i) not in self.DataCombo['values']:
                    self.DataCombo['values'] += (str(i),)
                if str(i) not in self.CLKCombo['values']:    
                    self.CLKCombo['values'] += (str(i),)
                if str(i) not in self.SSCombo['values']:    
                    self.SSCombo['values'] += (str(i),)
                
        self.cpol_var = IntVar()
        self.CB1 = Checkbutton(self.top, 
                               text='CPOL',
                               variable=self.cpol_var, 
                               onvalue=1, 
                               offvalue=0) #
        self.CB1.place(x = 150,y = 110)
        self.cpol_var.set(self.cpol) 
        
        self.cpha_var = IntVar()
        self.CB2 = Checkbutton(self.top, 
                               text='CPHA',
                               variable=self.cpha_var, 
                               onvalue=1, 
                               offvalue=0) #
        self.CB2.place(x = 150,y = 130)
        self.cpha_var.set(self.cpha) 
                
        self.Button = Button(self.top, 
                             text = "OK",
                             height=2, 
                             width=18, 
                             command = self.OkCallBack)
        self.Button.place(x = 80,y = 155)
        self.CLKCombo.current(0)
        self.DataCombo.current(0)
        self.SSCombo.current(0)
        
        self.top.protocol('WM_DELETE_WINDOW', self.exit_handler)
        self.top.mainloop()
    
    def decode(self,results,max_index,frequence):
        print (results[self.DataIn][100:4])
        self.decode_index =  []
        self.decode_state1 =  []
        self.decode_state2 =  []
        self.decode_index.append(0)
        self.decode_state1.append(1)
        self.decode_state2.append(0)
        self.bit_count = 0
        self.data = 0
        self.data_end_pos = 0
        self.decodeStrTmp = ""
        for i in range(1,max_index):
                
            if (results[self.SSIn][i-1]==1 and results[self.SSIn][i]==0 and self.bit_count == 0):#START
                self.add_point(i)                
                
                self.decodeStrTmp += "St"
                self.decode_position.append(i-((i-self.decode_index[-1])/2))
                self.decode_text.append(self.decodeStrTmp)
                self.decodeStrTmp = ""
                self.data = 0
                self.bit_count = 1
            elif (results[self.SSIn][i-1]==0 and results[self.SSIn][i]==1):#STOP
                self.decode_position.append(self.data_end_pos-((self.data_end_pos-self.decode_index[-1])/2))
                self.decodeStrTmp = str(hex(self.data))
                self.decode_text.append(self.decodeStrTmp)
                self.data = 0
                self.add_point(self.data_end_pos)#data end position
                
                self.decode_position.append(i-((i-self.decode_index[-1])/2))
                self.decodeStrTmp = "Sp"
                self.decode_text.append(self.decodeStrTmp)
                self.decodeStrTmp = ""
                self.add_point(i)
                self.bit_count = 0            
            elif(self.cpol == self.cpha and self.bit_count > 0  and results[self.CLKIn][i]==1 and results[self.CLKIn][i-1]==0):#DATA
                self.data = (self.data<<1) & results[self.DataIn][i]
                self.bit_count += 1
            elif(self.cpol == self.cpha and self.bit_count > 0  and results[self.CLKIn][i]==0 and results[self.CLKIn][i-1]==1):
                self.data = (self.data<<1) & results[self.DataIn][i]
                self.data_end_pos = i
            elif(self.cpol != self.cpha and self.bit_count > 0  and results[self.CLKIn][i]==0 and results[self.CLKIn][i-1]==1):#DATA
                self.data = (self.data<<1) & results[self.DataIn][i]
                self.bit_count += 1
            elif(self.cpol != self.cpha and self.bit_count > 0  and results[self.CLKIn][i]==1 and results[self.CLKIn][i-1]==0):
                self.data = (self.data<<1) & results[self.DataIn][i]
                self.data_end_pos = i
            elif(self.bit_count >= 128 and results[self.CLKIn][i]==0 and results[self.CLKIn][i-1]==1):
                self.bit_count = 1
                self.decode_position.append(i-((i-self.decode_index[-1])/2))
                self.decodeStrTmp = str(hex(self.data))
                self.decode_text.append(self.decodeStrTmp)
                self.data = 0
                self.add_point(i)

    
    def OkCallBack(self):
        self.DataIn = int(self.DataCombo.get())
        self.CLKIn = int(self.CLKCombo.get())
        self.SSIn = int(self.SSCombo.get())
        self.cpol = int(self.cpol_var.get())
        self.cpha = int(self.cpha_var.get())
        self.exit_handler()
    
    def exit_handler(self):
        #self.master.deiconify()
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
    app = spi(root)
    app.set_decode([1,1,1,1,1,1,1,1])
    