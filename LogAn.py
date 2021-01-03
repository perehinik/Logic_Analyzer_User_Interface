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
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
import ftd2xx #pip install ftd2xx
import os
import importlib

class i2c(Frame) :
    def __init__(self,master):
        self.master = master
        self.SclIn = 0
        self.SdaIn = 0
        
        self.decode_index  = []
        self.decode_state1 = []
        self.decode_state2 = []
        self.decode_position = []
        self.decode_text     = []
        
    def set_decode(self,channelStates):
        self.top = Toplevel(self.master)
        self.top.geometry("300x150")
        self.top.title("i2c") 
        self.top.grab_set()
        
        self.SDAlab = Label(self.top, text="SDA:")
        self.SDAlab.place(x = 80,y = 20)
        
        self.SCLlab = Label(self.top, text="SCL:")
        self.SCLlab.place(x = 80,y = 50)
        
        self.SdaCombo = Combobox(self.top, state="readonly",width = 8)
        self.SdaCombo.place(x = 140,y = 20)
        
        self.SclCombo = Combobox(self.top, state="readonly",width = 8)
        self.SclCombo.place(x = 140,y = 50)
        
        scl_in_temp = 100
        sda_in_temp = 100
        
        for i in range(0,len(channelStates)):
            if(channelStates[i] == 1 and i == self.SclIn):
                scl_in_temp = i
            if(channelStates[i] == 1 and i == self.SdaIn):
                sda_in_temp = i
                
        for i in range(0,len(channelStates)):
            if(channelStates[i] == 1 and scl_in_temp == 100):
                scl_in_temp = i
            if(channelStates[i] == 1 and sda_in_temp == 100):
                sda_in_temp = i
        
        if (scl_in_temp == 100):
            scl_in_temp = 0
        if (sda_in_temp == 100):
            sda_in_temp = 0    
        
        self.SclIn = scl_in_temp
        self.SdaIn = sda_in_temp
        
        self.SdaCombo['values'] += (str(self.SdaIn))
        self.SclCombo['values'] += (str(self.SclIn))
        for i in range(0,len(channelStates)):
            if (channelStates[i] == 1):
                if str(i) not in self.SdaCombo['values']:
                    self.SdaCombo['values'] += (str(i),)
                if str(i) not in self.SclCombo['values']:    
                    self.SclCombo['values'] += (str(i),)
                
        self.Button = Button(self.top, text = "OK",height=2, width=18, command = self.OkCallBack)
        self.Button.place(x = 80,y = 90)
        self.SclCombo.current(0)
        self.SdaCombo.current(0)
        
        self.top.protocol('WM_DELETE_WINDOW', self.exit_handler)
        self.top.mainloop()
    
    def decode(self,results,max_index,frequence):
        print (results[self.SdaIn][100:4])
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
        for i in range(1,max_index):
            if ((results[self.SclIn][i-1]==1 and results[self.SdaIn][i-1]==1) and 
                (results[self.SclIn][i]==1 and results[self.SdaIn][i]==0) and self.bit_count == 0):#START
                self.add_point(i)                
                
                self.decodeStrTmp += "St"
                self.decode_position.append(i-((i-self.decode_index[-1])/2))
                self.decode_text.append(self.decodeStrTmp)
                self.decodeStrTmp = ""
                self.bit_count = 1
            elif ((results[self.SclIn][i-1]==1 and results[self.SdaIn][i-1]==0) and 
                  (results[self.SclIn][i]==1 and results[self.SdaIn][i]==1)):#STOP
                self.decode_position.append(i-((i-self.decode_index[-1])/2))
                self.decodeStrTmp += "Sp"
                self.decode_text.append(self.decodeStrTmp)
                self.decodeStrTmp = ""
                
                self.add_point(i)
                
                self.bit_count = 0
            elif(self.bit_count > 0 and self.bit_count < 8 and results[self.SclIn][i]==1 and
                 results[self.SclIn][i-1]==0):#ADRESS
                if(self.bit_count==1):
                    self.data = 0
                    self.add_point(i)
                self.data = self.data<<1
                self.data += results[self.SdaIn][i]
                if(self.bit_count==7):
                    self.decodeStrTmp = str(hex(self.data))
                    self.data = 0
                self.bit_count += 1
            elif(self.bit_count == 8 and results[self.SclIn][i]==1 and results[self.SclIn][i-1]==0):#READ/WRITE
                if(results[self.SdaIn][i] == 1):
                    self.decodeStrTmp = self.decodeStrTmp + "+R"
                else:
                    self.decodeStrTmp = self.decodeStrTmp + "+W"
                
                self.decode_position.append(i-((i-self.decode_index[-1])/2))
                self.decode_text.append(self.decodeStrTmp)
                self.decodeStrTmp = ""
                
                self.bit_count = 30
            elif((self.bit_count == 9 or self.bit_count == 18) and results[self.SclIn][i]==1 and results[self.SclIn][i-1]==0):#ACK
                if(results[self.SdaIn][i] == 1):
                    self.decodeStrTmp = self.decodeStrTmp + "NACK"
                else:
                    self.decodeStrTmp = self.decodeStrTmp + "ACK"
                self.bit_count = 31
                
                self.decode_position.append(i-((i-self.decode_index[-1])/2))
                self.decode_text.append(self.decodeStrTmp)
                self.decodeStrTmp = ""
                
            elif(self.bit_count > 9 and self.bit_count < 18 and results[self.SclIn][i]==1 and results[self.SclIn][i-1]==0):#DATA
                if(self.bit_count==10):
                    self.data = 0
                self.data = (self.data<<1) & results[self.SdaIn][i]
                if(self.bit_count==17):
                    self.decodeStrTmp = str(hex(self.data))
                    self.data = 0
                self.bit_count += 1
            elif(self.bit_count == 30 and results[self.SclIn][i]==0 and results[self.SclIn][i-1]==1):
                self.bit_count = 9
                self.add_point(i)
            elif(self.bit_count == 31 and results[self.SclIn][i]==0 and results[self.SclIn][i-1]==1):
                self.bit_count = 10
                self.add_point(i)
    
    def OkCallBack(self):
        self.SdaIn = int(self.SdaCombo.get())
        self.SclIn = int(self.SclCombo.get())
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
    
class LogicAnaliser :
    def __init__(self,master) :
        self.master = master
        
        self.BLOCK_LEN = 2048 * 32

        self.RxTimerState = 1
        self.deviceIndex = -1
        self.dev = None
        self.rx_buffer = bytearray()
        
        self.timeout = 0;
        
        self.x  = np.arange(0, 30, 1)
        self.axis  = np.arange(25, 100, 1)
        self.z = [0] * 75
        
        self.index_max = 0
        self.results = []
        self.index = []
        for i in range(0,16):
            tempList = []
            self.results.append(tempList)
        
        self.startPosition = 0
        self.sampPitch = 1
        self.sampOnScreen = 30
        self.finishPosition = 0
        
        self.channelActiveMask = 0
        
        self.coreFrq = 300000000 #300MHz
        self.coreFrqPeriod = 1000000000/self.coreFrq
        self.sampFrq = 300000000.0
        self.AARate = 0;
        self.BBSamp = 0;
        self.HHTrigPos = 0;
        self.EEVolt = 0;
        
        self.decoder_instances = []
        self.dec_instance_state = []
        for i in range(0,8):
            inst_temp = i2c(self.master)
            self.decoder_instances.append(inst_temp)
            self.dec_instance_state.append("_")
        
        self.channel_count = 0
        self.channel_decode = [0]*16
        
        self.decode_count = 0
        self.decode_decode = [0]*8
        
        self.top1 = Frame(self.master, height = 500, width = 260, borderwidth=2,highlightbackground="gray" , highlightthickness=1)
        self.top1.pack(side="left", fill="both")
        self.top2 = Frame(self.master, height = 500, width = 500, borderwidth=2,highlightbackground="gray" , highlightthickness=1)
        self.top2.pack(side="right", fill="both")
        
        self.top_slider = Frame(self.top2, height = 5, width = 500)
        self.top_slider.pack(side="top", fill="x")
        
        self.plot_frame = Frame(self.top2) 
        self.plot_frame.pack(side="top", fill="both",expand = 1)
        
        self.right_slider = Frame(self.plot_frame)
        self.right_slider.pack(side="right", fill="y")
        
        self.AxisFrame = Frame(self.plot_frame, height = 5, width = 500)
        self.AxisFrame.pack(side="top")
        
        self.RSB1 = Button(self.right_slider, text = "+",height=1, width=4, command = self.zoomSliderP)
        self.RSB1.pack(side="top")
        
        self.w1 = Scale(self.right_slider, from_=1000, to=0,showvalue = 0,command = self.calcPosition)#command = self.calcPosition
        self.w1.set(0)
        self.w1.pack(side="top", fill="y",expand = 1)
        
        self.RSB2 = Button(self.right_slider, text = "-",height=1, width=4, command = self.zoomSliderM)
        self.RSB2.pack(side="top")
        
        self.w2 = Scale(self.top_slider, from_=0, to=100000, orient=HORIZONTAL, showvalue = 0,command = self.calcPosition) #command = self.calcPosition
        self.w2.set(0)

        self.SB1 = Button(self.top_slider, text = "<<<",height=1, width=3, command = self.shiftSliderMM)
        self.SB1.pack(side="left")
        self.SB2 = Button(self.top_slider, text = "<",height=1, width=3, command = self.shiftSliderM)
        self.SB2.pack(side="left")
        self.w2.pack(side="left", fill="both",expand=1)
        self.SB3 = Button(self.top_slider, text = ">>>",height=1, width=3, command = self.shiftSliderPP)
        self.SB3.pack(side="right")
        self.SB4 = Button(self.top_slider, text = ">",height=1, width=3, command = self.shiftSliderP)
        self.SB4.pack(side="right")
        
        self.AxisFig = plt.Figure(figsize=(25,2), dpi=100)
        self.AxisFig.set_figheight(0.25)
        self.AxisFig.subplots_adjust(left=-0.05, right=1.05, top=2, bottom=1)
        self.af = self.AxisFig.add_subplot(111)
        self.AxisFig.patch.set_facecolor('whitesmoke')
        self.af.axes.get_yaxis().set_visible(False)
        self.af.step(self.axis, self.z, where='post', label='post')
        self.af.set_frame_on(False)
        
        self.axVar = StringVar()
        self.axLab = Label(self.AxisFrame, textvariable=self.axVar,height = 1,width=2)
        self.axVar.set("sp")
        self.axLab.pack(side="left")
        
        self.AxCanvas = FigureCanvasTkAgg(self.AxisFig, self.AxisFrame)
        self.AxCanvas.get_tk_widget().pack(side = "left",pady=2)
        

        self.decode_frame = Frame(self.plot_frame) 
        self.decode_frame.pack(side="top", fill="both",expand = 0)
        self.channel_frame = Frame(self.plot_frame) 
        self.channel_frame.pack(side="top", fill="both",expand = 0)#<-----------------------------
        
        self.plot_frames = []
        for i in range(0,16):
            self.plotFrame = Frame(self.channel_frame)
            self.plot_frames.append(self.plotFrame)
        
        self.decode_frames = []
        for i in range(0,8):
            self.decodeFrame = Frame(self.decode_frame)
            self.decode_frames.append(self.decodeFrame)

        self.plot_figures = []
        self.plot_axes = []
        self.plot_canvases = []
        self.plot_labels = []
        self.plot_label_values = []
        for i in range(0,16):
            
            self.figure = plt.Figure(figsize=(25,2), dpi=150)
            self.plot_figures.append(self.figure)
            self.plot_figures[i].set_figheight(0.2)#<------------------------------------------------
            self.plot_figures[i].subplots_adjust(left=-0.05, right=1.05, top=1, bottom=0)
            self.plot_figures[i].patch.set_visible(False)
            
            self.ax = self.plot_figures[i].add_subplot(111)
            self.plot_axes.append(self.ax)
            self.canvas = FigureCanvasTkAgg(self.plot_figures[i], self.plot_frames[i])
            self.plot_canvases.append(self.canvas)
            
            self.insideVar = StringVar()
            self.plot_label_values.append(self.insideVar)
            self.plot_label_values[i].set(str(i))
            self.plotLabel = Label(self.plot_frames[i], textvariable=self.plot_label_values[i],height = 1,width=2)
            self.plot_labels.append(self.plotLabel)
            self.plot_labels[i].pack(side="left")
            
            self.plot_canvases[i].get_tk_widget().pack(side="right", fill="both", expand=1,pady=2)
        
        self.decode_figures = []
        self.decode_axes = []
        self.decode_canvases = []
        self.decode_labels = []
        self.decode_label_values = []
        for i in range(0,8):
            
            self.figure = plt.Figure(figsize=(25,2), dpi=100)
            self.decode_figures.append(self.figure)
            self.decode_figures[i].set_figheight(0.3)
            self.decode_figures[i].subplots_adjust(left=-0.05, right=1.05, top=1, bottom=0)
            self.decode_figures[i].patch.set_visible(False)
            
            self.ax = self.decode_figures[i].add_subplot(111)
            self.decode_axes.append(self.ax)
            self.canvas = FigureCanvasTkAgg(self.decode_figures[i], self.decode_frames[i])
            self.decode_canvases.append(self.canvas)
            
            self.insideVar = StringVar()
            self.decode_label_values.append(self.insideVar)
            self.decode_label_values[i].set(str(i+1))
            self.decodeLabel = Label(self.decode_frames[i], textvariable=self.decode_label_values[i],height = 1,width=2)
            self.decode_labels.append(self.decodeLabel)
            self.decode_labels[i].pack(side="left")
            
            self.decode_canvases[i].get_tk_widget().pack(side="right", fill="both", expand=1,pady=2)
        
        
        self.BStart = Button(self.top1, text = "Start",height=2, width=30, command = self.StartCallBack)
        self.BStart.place(x = 20,y = 10)
        
        self.L2var = StringVar()
        self.L2 = Label(self.top1, textvariable=self.L2var)
        self.L2var.set("Duration:")
        self.L2.place(x = 20,y = 70)
        
        self.STB1var = StringVar()
        self.STB1var.set("255")
        self.STB1 = Entry(self.top1, width=11,textvariable = self.STB1var)
        self.STB1.place(x = 85,y = 70)
        
        self.comboDuration = Combobox(self.top1, 
                                    values=[
                                            "samp", 
                                            "sec",
                                            "msec",
                                            "usec",
                                            "nsec"],
                                    state="readonly",
                                    width = 8)
        self.comboDuration.place(x = 170,y = 70)
        self.comboDuration.current(0)
        
        self.L3var = StringVar()
        self.L3 = Label(self.top1, textvariable = self.L3var)
        self.L3var.set("Samp. rate:")
        self.L3.place(x = 20,y = 90)
        
        self.STB2var = StringVar()
        self.STB2var.set("300")
        self.STB2 = Entry(self.top1, width=11,textvariable = self.STB2var)
        self.STB2.place(x = 85,y = 90)
        
        self.comboRate = Combobox(self.top1, 
                                    values=[
                                            "Hz", 
                                            "kHz",
                                            "MHz"],
                                    state="readonly",
                                    width = 8)
        self.comboRate.place(x = 170,y = 90)
        self.comboRate.current(2)
        
        self.L6var = StringVar()
        self.L6 = Label(self.top1, textvariable=self.L6var)
        self.L6var.set("Input threshold, V:")
        self.L6.place(x = 20,y = 110)
        
        self.STB3var = StringVar()
        self.STB3var.set("3")
        self.STB3 = Entry(self.top1, width=11,textvariable = self.STB3var)
        self.STB3.place(x = 170,y = 110)
        
        self.var1 = IntVar()
        self.CB1 = Checkbutton(self.top1, text='Trigger',variable=self.var1, onvalue=1, offvalue=0, command=self.TriggerCallBack) #
        self.CB1.place(x = 20,y = 145)
        
        self.L4var = StringVar()
        self.L4 = Label(self.top1, textvariable=self.L4var)
        self.L4var.set("Trigger type:")
        self.L4.place(x = 20,y = 165)
        
        self.comboTriggerT = Combobox(self.top1, 
                                    values=["Rising edge",
                                            "Falling edge",
                                            "High", 
                                            "Low"],
                                    state="disabled",
                                    width = 15)
        self.comboTriggerT.place(x = 125,y = 165)
        self.comboTriggerT.current(0)
        
        self.L5var = StringVar()
        self.L5 = Label(self.top1, textvariable=self.L5var)
        self.L5var.set("Trigger channel:")
        self.L5.place(x = 20,y = 185)
        
        self.comboTriggerCh = Combobox(self.top1, 
                                    values=["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"],
                                    state="disabled",
                                    width = 15)
        self.comboTriggerCh.place(x = 125,y = 185)
        self.comboTriggerCh.current(0)

        self.channel_active_int = []
        for i in range(0,16):
            self.channel_active_int.append(0)
            
        self.decode_active_int = []
        for i in range(0,8):
            self.decode_active_int.append(0)
        
        self.L61var = StringVar()
        self.L61 = Label(self.top1, textvariable=self.L61var)
        self.L61var.set("Samp. before trig:")
        self.L61.place(x = 20,y = 205)
        
        self.STB31var = StringVar()
        self.STB31var.set("3")
        self.STB31 = Entry(self.top1, width=18,state="disabled",textvariable = self.STB31var)
        self.STB31.place(x = 125,y = 205)
        
        self.L7var = StringVar()
        self.L7 = Label(self.top1, textvariable=self.L7var)
        self.L7var.set("Channels:")
        self.L7.place(x = 20,y = 240)
        
        self.channel_active = []
        self.channel_ch_box = []
        for i in range(0,16):
            self.chAct = IntVar()
            self.channel_active.append(self.chAct)
            self.chActChB = Checkbutton(self.top1, text=str(i),variable=self.channel_active[i], onvalue=1, offvalue=0, command=self.RefreshCh)
            self.channel_ch_box.append(self.chActChB)
            self.channel_ch_box[i].place(x = 20+(i%4)*60,y = 260+(i//4)*20)
        
        self.L8var = StringVar()
        self.L8 = Label(self.top1, textvariable=self.L8var)
        self.L8var.set("Decoders:")
        self.L8.place(x = 20,y = 355)
        
        self.decode_cb = []
        self.decode_cb_var = []
        self.decode_combo = []
        self.decode_buttons = []
        for i in range(0,8):
            dec_cb = IntVar()
            self.decode_cb_var.append(dec_cb)
            decActChB = Checkbutton(self.top1, text=str(i+1),variable=self.decode_cb_var[i], onvalue=1, offvalue=0, command=self.ResetDecodes) #
            self.decode_cb.append(decActChB)
            self.decode_cb[i].place(x = 20,y = 375+(i*28))
            decodeCombo = Combobox(self.top1, values=["i2c"],state="disabled",width = 20)
            self.decode_combo.append(decodeCombo)
            self.decode_combo[i].place(x = 60,y = 375+(i*28))
            self.decode_combo[i].current(0)
            self.decode_combo[i].bind("<<ComboboxSelected>>", self.ComboUpdate)
            self.decodeButton = Button(self.top1, text = "set",height=1, width=3, state="disabled")
            self.decode_buttons.append(self.decodeButton)
            self.decode_buttons[i].place(x = 210,y = 372+(i*28))            
            self.decode_buttons[i].configure(command=lambda:self.decoder_instances[i].set_decode(self.channel_active_int))
        
        self.BDecode = Button(self.top1, text = "Decode",height=2, width=30, command = self.ResetDecodes)
        self.BDecode.place(x = 20,y = 600)
        
        self.BFill = Button(self.top1, text = "Fill",height=2, width=13, command = self.FillCallBack)
        self.BFill.place(x = 20,y = 650)
        
        self.BSort = Button(self.top1, text = "Sort",height=2, width=13, command = self.SortCallBack)
        self.BSort.place(x = 140,y = 650)
        
        for root, dirs, files in os.walk("."):
            for filename in files:
                if(filename[0:3]== "la_" and filename[-3:]== ".py"):
                    print(filename)
                    module_name = filename[3:len(filename)-3]
                    for i in range(0,8):
                        if module_name not in self.decode_combo[i]['values']:
                            self.decode_combo[i]['values'] += (module_name,)    
        
        
        self.drawDecodes([1,0,0,0,0,0,0,0],0)
        self.drawPlots([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],1,1)
        self.drawDecodes([0,0,0,0,0,0,0,0],0)
        
        
        self.master.protocol("WM_DELETE_WINDOW",self.exit_handler)
    
    def calcPosition(self,*args):
        sampOnScreenMin = 30
        sampOnScreenMax = 10000
        self.index_max = 0
        for i in range(0,16):
            if(self.index_max < len(self.results[i])):
               self.index_max = len(self.results[i])
        
        if (self.index_max > sampOnScreenMin and self.index_max < sampOnScreenMax):
            self.sampOnScreen = sampOnScreenMin + int(((self.index_max-sampOnScreenMin) / 1000) * (1000-self.w1.get()))
        elif (self.index_max > sampOnScreenMax):
            self.sampOnScreen = sampOnScreenMin + int(((sampOnScreenMax-sampOnScreenMin) / 1000) * (1000-self.w1.get()))
        else:
            self.sampOnScreen = self.index_max
            
        self.sampPitch = (self.sampOnScreen // 1000) +1#
        
        if (self.index_max > sampOnScreenMin):
            self.startPosition = int((self.index_max - self.sampOnScreen)/100000 * self.w2.get())
        else:
            self.startPosition = 0
        
        self.finishPosition = self.startPosition + self.sampOnScreen
        self.drawPlots(self.channel_active_int,0,0)
    
    def RefreshCh(self):
        for i in range(0,16):
            if(self.index_max < len(self.results[i])):
               self.index_max = len(self.results[i])
               
        for i in range(0,16):
            if(len(self.results[i])<self.index_max and self.channel_active[i].get() == 1):
                self.results[i] = [0]*self.index_max

        self.calcPosition()
        self.ResetPlots()
    
    def ResetPlots(self):
        self.channelActiveMask = 0
        self.channel_count = 0
        for i in range(0,16):
            self.channel_active_int[i] = self.channel_active[i].get()
            if(self.channel_active_int[i]==1):
                self.channel_count += 1
                self.channel_decode[i] = self.channel_count-1
        for i in range(0,16):
            self.channelActiveMask = (self.channelActiveMask << 1) | self.channel_active_int[15-i]
        print(self.channel_active_int)
        self.drawPlots(self.channel_active_int,1,0)

    def ResetDecodes(self):
        self.decodeActiveMask = 0
        self.decode_count = 0
        for i in range(0,8):
            self.decode_active_int[i] = self.decode_cb_var[i].get()
            if(self.decode_active_int[i]==1):
                self.decode_count += 1
                self.decode_decode[i] = self.decode_count-1
                self.decode_combo[i]["state"] = "readonly"
                self.decode_buttons[i]["state"] = "normal"
            else:
                self.decode_combo[i]["state"] = "disabled"
                self.decode_buttons[i]["state"] = "disabled"
        self.UpdateDecodeInstances()
        for i in range(0,8):
            if(self.decode_active_int[i] == 1):
                self.decoder_instances[i].decode(self.results,self.index_max,self.sampFrq)
        self.drawDecodes(self.decode_active_int,0)
                  
    def drawPlots(self,plot_state,refreshFlag,sortFlag):
        
        self.index = np.arange(0, self.index_max, 1)
        self.z = [0] * self.index_max
        
        self.af.clear()
        self.af.axes.get_yaxis().set_visible(False)
        self.af.step(self.index[self.startPosition:self.finishPosition:1], 
                     self.z[self.startPosition:self.finishPosition:1],
                                 where='post', label='post')
        self.af.set_frame_on(False)

        self.AxCanvas.draw()
        self.AxisFrame.pack(side="top")
        
        if(sortFlag == 1):
            for i in range(0,16): 
                self.plot_frames[i].pack_forget()
        
        for i in range(0,16):     
            if(refreshFlag == 1):
                self.plot_axes[i].clear()
                self.plot_figures[i].patch.set_visible(False)
            
            if(plot_state[i]==1):
                self.plot_axes[i].clear()
                self.plot_figures[i].patch.set_visible(False)
                self.plot_axes[i].step(self.index[self.startPosition:self.finishPosition:1], #self.sampPitch
                                                  self.results[i][self.startPosition:self.finishPosition:1], #self.sampPitch
                                                  where='post', label='post')
                self.plot_axes[i].set_ylim(-0.01,1.01)
                self.plot_axes[i].axis('off')

                self.plot_canvases[i].draw()
                self.plot_canvases[i].get_tk_widget().update_idletasks()
                if(refreshFlag == 1):
                    self.plot_frames[i].pack(side="top", fill="both", expand=1)
            elif(refreshFlag == 1):
                self.plot_frames[i].pack_forget()
        self.ResetDecodes()
    
    def drawDecodes(self,decode_state,sortFlag):
        if(sortFlag == 1):
            for i in range(0,8): 
                self.decode_frames[i].pack_forget()  
                
        for i in range(0,8):
            self.decode_axes[i].clear()
            self.decode_figures[i].patch.set_visible(False)
            
            if(decode_state[i]==1):
                self.decode_ind_temp = []
                self.decode_state1_temp = []
                self.decode_state2_temp = []
                
                if(len(self.decoder_instances[i].decode_index)>0):
                    for f in range(0,len(self.decoder_instances[i].decode_index)):
                        if(self.decoder_instances[i].decode_index[f] > self.startPosition+0.5 and self.decoder_instances[i].decode_index[f] < self.finishPosition-0.5):
                           self.decode_ind_temp.append(self.decoder_instances[i].decode_index[f])
                           self.decode_state1_temp.append(self.decoder_instances[i].decode_state1[f])
                           self.decode_state2_temp.append(self.decoder_instances[i].decode_state2[f])
                    
                if(len(self.decode_ind_temp)==0):
                    self.decode_ind_temp.append(self.startPosition)
                    self.decode_state1_temp.append(0)
                    self.decode_state2_temp.append(1)

                self.decode_ind_temp.insert(0,self.startPosition)
                self.decode_state1_temp.insert(0,self.decode_state1_temp[0])
                self.decode_state2_temp.insert(0,self.decode_state2_temp[0])
    
                self.decode_ind_temp.append(self.finishPosition)
                self.decode_state1_temp.append(self.decode_state1_temp[-1])
                self.decode_state2_temp.append(self.decode_state2_temp[-1])                
                
                self.decode_axes[i].plot(self.decode_ind_temp, self.decode_state1_temp, color='r')
                self.decode_axes[i].plot(self.decode_ind_temp, self.decode_state2_temp, color='r')
                self.decode_axes[i].set_ylim(-0.01,1.01)
                self.decode_axes[i].axis('off')
                for d in range(0,len(self.decoder_instances[i].decode_position)):
                    self.decode_axes[i].text(self.decoder_instances[i].decode_position[d],0.1,self.decoder_instances[i].decode_text[d], fontsize=10)
                self.decode_canvases[i].draw()
                self.decode_frames[i].pack(side="top", fill="both", expand=1)
            else:
                self.decode_frames[i].pack_forget()

    def TriggerCallBack(self):
        if(self.var1.get() == 1):
            self.comboTriggerCh["state"] = "readonly"
            self.comboTriggerT["state"] = "readonly"
            self.STB31["state"] = "normal"
        else:
            self.comboTriggerCh["state"] = "disabled"
            self.comboTriggerT["state"] = "disabled"
            #self.STB31var.set(3)
            self.STB31["state"] = "disabled"

    def ft_init(self):
        #Get the device list and save the index of logic analiser into deviceIndex
        self.deviceList = ftd2xx.listDevices(0) # returns the list of ftdi devices S/Ns 
        self.deviceIndex = -1;
        self.status = -1;
        if self.deviceList : 
             print(len(self.deviceList), 'ftdi devices found')
             for x in range(0,len(self.deviceList)):
                 if ( "LogicAnaliser" in str(ftd2xx.getDeviceInfoDetail(x)['description'])) :
                     print("Device %d details: "%x)
                     print('-------------------------------------------------')
                     print("Serial : " + str(ftd2xx.getDeviceInfoDetail(x)['serial']))
                     print("Type : "  + str(ftd2xx.getDeviceInfoDetail(x)['type']))
                     print("ID : " + str(ftd2xx.getDeviceInfoDetail(x)['id']))
                     print("Description : " + str(ftd2xx.getDeviceInfoDetail(x)['description']))
                     print('-------------------------------------------------')
                     
                     if self.deviceIndex < 0:
                         self.deviceIndex = x
                     break
        else:
             print("no ftdi devices connected")
     
    def connect(self):
        if self.deviceIndex >= 0 :
             print('Connecting to device with index %d'% self.deviceIndex)
             self.dev = ftd2xx.open(self.deviceIndex) #FT4HNA7Z
             self.status = 1
             time.sleep(0.1)
             self.dev.setBitMode(0x00, 0x40)
             
             print('Device connected')
       
        elif ftd2xx.listDevices(0):
             print("no FTDI devices to be connected")
             self.messagebox.showinfo(title=None, message="Logic Analiser was not found")


    def disconnect(self):
        self.dev.close()
        print("Device disconnected")

    def timerHandler(self): 
        self.read()
        print("check if all data collected %d"%len(self.rx_buffer))
        print("needed %d"%(self.BBSamp-self.BBSamp*0.01))
        if (len(self.rx_buffer) < (self.BBSamp-self.BBSamp*0.01) and (self.timeout < 50 or self.var1.get() == 1)) :
            self.timeout += 1
            self.master.after(1, self.timerHandler)
        else:
            print("data collected") 
            self.disconnect()
            self.w1.set(0)
            self.w2.set(0)
            self.calcPosition()
            
    def send(self):
        
        print("Send data")
        self.tx_data =  "#>HH"
        self.tx_data =  "#$FF" + self.HHTrigPosStr 
        self.tx_data += "#$EE" + self.EEVoltStr
        self.tx_data += "#$AA" + self.AARateStr
        self.tx_data += "#$BB" + self.BBSampStr
        self.tx_data += "#$CC" + self.CCTrigStr
        self.tx_data += "#$DD" + self.DDMaskStr
        self.tx_data += "#>GG"
        self.tx_data = self.tx_data.upper()
        self.tx_data += self.tx_data
        for a in range(0,16):
            self.results[a] = []
        
        print(self.tx_data)        
        b=bytearray()
        b.extend(map(ord,self.tx_data))
        if len(self.tx_data)>0 :
            print("\r\nSending %d bytes:"%len(self.tx_data))
            print('-------------------------------------------------')
            print(self.tx_data)
            print('-------------------------------------------------')
            self.written = self.dev.write(self.tx_data)
        else :
            print("Please enter data into a top text field")
        #self.timer1.start()
        self.timeout = 0
        self.rx_buffer = bytearray()
        self.timerHandler()

    def read(self):
        rx_data = bytearray()

        while self.dev.getQueueStatus()>0 :
             rx_data = self.dev.read(self.dev.getQueueStatus())

        if len(rx_data)>0 :
            self.rx_buffer += rx_data
            print("\r\nReceived %d bytes:"%len(rx_data))
            print('-------------------------------------------------')
            self.timeout = 0 # reset timeout if some data received
            if(self.channel_count <= 8):
                for i in range(0,len(rx_data),1):
                    x = bytearray()
                    x.append(rx_data[i]);
                
                    if(self.channel_count <= 2):
                        for ind in range(0,16):
                            if(self.channel_active_int[ind] == 1):
                                self.results[ind].append((int(int.from_bytes(x, byteorder='big', signed=False)>>self.channel_decode[ind]+6)&1))
                                self.results[ind].append((int(int.from_bytes(x, byteorder='big', signed=False)>>self.channel_decode[ind]+4)&1))
                                self.results[ind].append((int(int.from_bytes(x, byteorder='big', signed=False)>>self.channel_decode[ind]+2)&1))
                                self.results[ind].append((int(int.from_bytes(x, byteorder='big', signed=False)>>self.channel_decode[ind])&1))
                    elif(self.channel_count <= 4):
                        for ind in range(0,16):
                            if(self.channel_active_int[ind] == 1):
                                self.results[ind].append((int(int.from_bytes(x, byteorder='big', signed=False)>>self.channel_decode[ind]+4)&1))
                                self.results[ind].append((int(int.from_bytes(x, byteorder='big', signed=False)>>self.channel_decode[ind])&1))
                    elif(self.channel_count <= 8):
                        for ind in range(0,16):
                            if(self.channel_active_int[ind] == 1):
                                self.results[ind].append((int(int.from_bytes(x, byteorder='big', signed=False)>>self.channel_decode[ind])&1))
            elif(self.channel_count > 8 and self.channel_count <= 16):
                for i in range(0,len(rx_data)//2,2):
                    for ind in range(0,16):
                        x = bytearray()
                        x.append(rx_data[i])
                        x.append(rx_data[i+1])
                        self.results[ind].append((int(int.from_bytes(x, byteorder='big', signed=False)>>ind)&1))

    def updSet(self):
        temp1 = 1
        
        ##AA DATA RATE
        if (self.comboRate.get() == "Hz"):
            temp1 = 1
        elif(self.comboRate.get() == "kHz"):
            temp1 = 1000    
        elif(self.comboRate.get() == "MHz"):
            temp1 = 1000000
        
        self.AARate = self.coreFrq // (float(self.STB2var.get())*temp1)-1
        if (self.AARate > 16777215):
            self.AARate = 16777215
        elif(self.AARate < 0):
            self.AARate = 0
        self.sampFrq = self.coreFrq / ((self.AARate+1)*temp1)
        self.STB2var.set(str(self.sampFrq))
        self.sampFrq = self.coreFrq / (self.AARate+1)
        
        AARateByte = hex(int(self.AARate))
        self.AARateStr = str(AARateByte)
        self.AARateStr = self.AARateStr[2:]
        for ind in range(0,6-len(self.AARateStr)):
            self.AARateStr = '0' + self.AARateStr
        print("AA(Frq) = %d"%self.AARate)
        print(self.AARateStr)
        
        ##BB DURATION
        if (self.comboDuration.get() == "samp"):
            self.BBSamp = float(self.STB1var.get()) // 1
            self.STB1var.set(str(int(self.BBSamp)))
        else:
            if (self.comboDuration.get() == "sec"):
                temp1 = 1000000000
            elif(self.comboDuration.get() == "msec"):
                temp1 = 1000000    
            elif(self.comboDuration.get() == "usec"):
                temp1 = 1000
            elif(self.comboDuration.get() == "nsec"):
                temp1 = 1
            self.BBSamp = (temp1 * float(self.STB1var.get())) // self.coreFrqPeriod
            self.BBSamp += 1
            
        if(self.channel_count>0 and self.channel_count<=2):
            self.BBSamp = self.BBSamp / 4
            print("2")
        elif(self.channel_count>2 and self.channel_count<=4):
            self.BBSamp = self.BBSamp / 2
            print("4")
        elif(self.channel_count>8):
            self.BBSamp = self.BBSamp * 2
            print("16")
        
        if (self.BBSamp > 16777215):
            self.BBSamp = 16777215
        elif(self.BBSamp < 0):
            self.BBSamp = 0

        BBSampByte = hex(int(self.BBSamp))
        self.BBSampStr = str(BBSampByte)
        self.BBSampStr = self.BBSampStr[2:]
        for ind in range(0,6-len(self.BBSampStr)): #fill most sign bits with 0
            self.BBSampStr = '0' + self.BBSampStr
        print("BB(Samp) = %d"%self.BBSamp)
        print(self.BBSampStr)
        
        #CC TRIGGER CH
        if (self.var1.get() == 1):
            if(self.comboTriggerT.get()=="Rising edge"):
                CCTrigTStr = '0'
            elif(self.comboTriggerT.get()=="Falling edge"):
                CCTrigTStr = '1'
            elif(self.comboTriggerT.get()=="High"):
                CCTrigTStr = '2'
            elif(self.comboTriggerT.get()=="Low"):
                CCTrigTStr = '3'
        else: 
            CCTrigTStr = 'F'
            
        CCTrigChByte = hex(int(self.comboTriggerCh.get()))
        CCTrigChStr = str(CCTrigChByte)    
        self.CCTrigStr = "0000" + CCTrigTStr + CCTrigChStr[2:]
        print("CC(TrigCh) = %d"%int(self.comboTriggerCh.get()))
        print(self.CCTrigStr)
        
        #HH TRIGGER POSITION
        self.HHTrigPos = int(self.STB31var.get())
        
        if(self.channel_count>0 and self.channel_count<=2):
            self.HHTrigPos = self.HHTrigPos // 8
            print("2")
        elif(self.channel_count>2 and self.channel_count<=4):
            self.HHTrigPos = self.HHTrigPos // 4
            print("4")
        elif(self.channel_count>4 and self.channel_count<=8):
            self.HHTrigPos = self.HHTrigPos // 2
            print("8")
        
        if (self.HHTrigPos > 64000):
            self.HHTrigPos = 64000
        elif(self.HHTrigPos < 0):
            self.HHTrigPos = 0
        
        HHTrigPosByte = hex(self.HHTrigPos)
        self.HHTrigPosStr = str(HHTrigPosByte)
        self.HHTrigPosStr = self.HHTrigPosStr[2:]
        for ind in range(0,6-len(self.HHTrigPosStr)):
            self.HHTrigPosStr = '0' + self.HHTrigPosStr
        print("РР(TrigPos) = %d"%self.HHTrigPos)
        print(self.HHTrigPosStr)
        
        
        #DD CH BITMAP
        DDMaskByte = hex(self.channelActiveMask)
        self.DDMaskStr = str(DDMaskByte)
        self.DDMaskStr = self.DDMaskStr[2:]
        for i in range(0,6-len(self.DDMaskStr)):
            self.DDMaskStr = '0' + self.DDMaskStr
        print("DD(Mask) = %d"%self.channelActiveMask)
        print(self.DDMaskStr)
        
        #EE VOLTAGE
        EEVoltFl = float(self.STB3var.get())
        if (EEVoltFl > 5):
            self.STB3var.set("5")
        if (EEVoltFl > 3.6):    
            EEVoltFl = 3.6
        elif (EEVoltFl < 0.6):
            self.STB3var.set("0.6")
            EEVoltFl = 0.6
        self.EEVolt = (EEVoltFl-0.6) * 65
        self.EEVolt = int(255 - self.EEVolt)
        
        EEVoltByte = hex(self.EEVolt)
        self.EEVoltStr = str(EEVoltByte)    
        self.EEVoltStr = "0000" + self.EEVoltStr[2:]
        
        print("EE(Volt) = %d"%self.EEVolt)
        print(self.EEVoltStr)
 
    def StartCallBack(self):
        self.updSet()
        self.ft_init()
        self.connect()
        self.send()
    
    def FillCallBack(self):
        self.decode_frame.pack_forget()
        self.channel_frame.pack_forget()
        if(self.BFill['text'] == "Fill"):
            self.BFill['text'] = "standart view"
            self.decode_frame.pack(side="top", fill="both",expand = 1)
            self.channel_frame.pack(side="top", fill="both",expand = 1)
        else:
            self.BFill['text'] = "Fill"
            self.decode_frame.pack(side="top", fill="both",expand = 0)
            self.channel_frame.pack(side="top", fill="both",expand = 0)
        
    def SortCallBack(self):
        self.drawDecodes(self.decode_active_int,1)
        self.drawPlots(self.channel_active_int,1,1)
                
    def ComboUpdate(self,event):
        self.UpdateDecodeInstances()
        
    def UpdateDecodeInstances(self):
        for i in range(0,8):
            if(self.dec_instance_state[i] != self.decode_combo[i].get() and self.decode_cb_var[i].get() == 1):
                self.dec_instance_state[i] = self.decode_combo[i].get()
                if(self.decode_combo[i].get() == "i2c"):
                    self.decoder_instances[i] = i2c(self.master)
                else:
                    filename = "la_" + self.decode_combo[i].get()
                    module = importlib.import_module(filename)
                    class_ = getattr(module, filename[3:])
                    self.decoder_instances[i] = class_(self.master)
                    
                self.decode_buttons[i].configure(command=lambda x=i :self.setDecode(x))
    
    def setDecode(self,ch):
        self.decoder_instances[ch].set_decode(self.channel_active_int)
        
    def zoomSliderP(self):
        temp = self.w1.get()
        temp += 1
        self.w1.set(temp)
    
    def zoomSliderM(self):
        temp = self.w1.get()
        temp -= 1
        self.w1.set(temp)
        
    def shiftSliderMM(self):
        temp1 = self.index_max/100000
        temp2 = int(self.sampOnScreen/temp1)
        temp = self.w2.get()
        temp -= temp2
        self.w2.set(temp)
    def shiftSliderM(self):
        temp1 = self.index_max/100000
        temp2 = int(self.sampOnScreen/temp1/10)
        temp = self.w2.get()
        temp -= temp2
        self.w2.set(temp)
    def shiftSliderP(self):
        temp1 = self.index_max/100000
        temp2 = int(self.sampOnScreen/temp1/10)
        temp = self.w2.get()
        temp += temp2
        self.w2.set(temp)
    def shiftSliderPP(self):
        temp1 = self.index_max/100000
        temp2 = int(self.sampOnScreen/temp1)
        temp = self.w2.get()
        temp += temp2
        self.w2.set(temp)
   
    def disconnectCallBack(self):
        self.disconnect()

    def sendCallBack(self):
        self.send()
    
    def exit_handler(self):
        #disconnect() #add checking if connected
        self.drawPlots([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],1,0)
        self.drawDecodes([0,0,0,0,0,0,0,0],0)
        print('Bye! :)')
        self.master.destroy()
        
def main(): 
    root = Tk()
    root.geometry("1250x700")
    root.wm_title("LogicAnaliser")
    app = LogicAnaliser(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()    
 