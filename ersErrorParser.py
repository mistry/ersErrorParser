#!/usr/bin/python

import argparse
import getsb
import dbhandler
from numpy import array 
from collections import OrderedDict
from ROOT import TH1F, kBlue, kRed, TCanvas, gROOT, THStack, TLegend, gStyle, kBird, TMultiGraph, TGraph, gPad, kBlack, TLine, kPink, kMagenta, kOrange, kGreen, kCyan, kYellow, TColor, kCMYK, kBlueRedYellow, kRainBow
import AtlasStyle


error_bits = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e']

rod_numbers = {'0x311e00_1':3893, 
               '0x311f00_1':500,'0x311f00_2': 2050, 
               '0x321100_1':5226,
               '0x321600_1':4910,
               '0x322000_1':3291,
               '0x330b01_1':4957,'0x330b01_2': 5003, 
               '0x331801_1':4910,
               '0x331c02_1':4910,
               '0x341302_1':4910,
               '0x341401_1':4013, '0x341401_1':4910,
               }
rod_titles = {'0x311e00_1':'ROD replacement', 
              '0x311f00_1':'GOL cable fix', '0x311f00_2':'ROD replacement', 
              '0x321100_1':'ROD PP Swap',
              '0x321600_1':'GOL cable re-seat',
              '0x322000_1':'ROD PP replacement',
              '0x330b01_1':'ROD PP replacement', '0x330b01_2':'ROD PP replacement', 
              '0x331801_1':'ROD and Cable re-seat',
              '0x331c02_1':'ROD Swap',
              '0x341302_1':'ROD PP replacement',
              '0x341401_1':'GOL cable swap', '0x341401_1':'ROD Swap',
              }

def main():

    AtlasStyle.SetAtlasStyle()
    gROOT.SetBatch()
  
    parser = argparse.ArgumentParser(description='Error Analysis for TRT logs, input grafana mu dumps and ers log.')
    parser.add_argument('-d', '--dir', dest='dir', default='2018', type=str,  help="Directory of grafana mu dumps")
    parser.add_argument('-f', '--file', dest='log_file', default='', type=str, help="Log file from ERS.")
    parser.add_argument('-s', '--print_sb', dest='print_sb', default=False, action='store_true', help="print sb times")
    parser.add_argument('-n', '--non_sb',dest='non_sb', default=False, action='store_true', help="get errors for non-sb times")
    parser.add_argument('-t', '--text',dest='text_filter', default='rocketio problem', type=str, help="text to filter query")
    parser.add_argument('-b', '--date_beg',dest='date_beg', default='2015-04-01 00:00:00', type=str, help="date begin. Formatted yyyy-mm-dd hh:mm:ss format")
    parser.add_argument('-e', '--date_end',dest='date_end', default='2100-01-01 00:00:00', type=str, help="date end.  Formatted yyyy-mm-dd hh:mm:ss format")

    args = parser.parse_args()

    if args.print_sb:
        beg_sb, end_sb = getsb.get_sb_list(args.dir, args.print_sb)

    if args.log_file != '':
        beg_sb, end_sb = getsb.get_sb_list(args.dir, args.print_sb)
        dbhandler.add_to_db(beg_sb, end_sb, args.log_file)

    query_errors = dbhandler.get_query(args.non_sb, args.text_filter, args.date_beg, args.date_end)
    print "Query returned " + repr(len(query_errors)) + " results!"

    if('rocketio' in args.text_filter):
        parse_rocketio_errors(query_errors)

def parse_rocketio_errors(results):

    rode_dict_buff = {}
    rode_dict_lock = {}
    rod_dict_buff = {}
    rod_dict_lock = {}
    
    sb_suf = "_nonsb"
    if(results[0].sb == 1):
        sb_suf = "_sb"

    for error in results:

        #print error.date, error.sb_total_time, error.sb_time_run, error.sb_length
        #cool magic numbers, because string looks like
        #ROD 0x320900: rocketio problem: Lock status == 0xf , buffer status == 0x5
        pos_rod  = error.text.find("ROD") + 4
        pos_lock = error.text.find("Lock") + 15
        pos_buff = error.text.find("buffer") + 17
       
        if error.msgID == 'TRT::ROD05Module':
            rod  = '0x'+str(error.text[pos_rod:pos_rod+6])
        else:
            rod  = str(error.text[pos_rod:pos_rod+8])

        lock = str(error.text[pos_lock:pos_lock+3])
        buff = str(error.text[pos_buff:pos_buff+3])
        bin_lock = bin(int(lock, 16))[2:].zfill(4)
        bin_buff = bin(int(buff, 16))[2:].zfill(4)

        if buff == '0xf':
            if not rod+'_'+lock in rode_dict_lock:
                rode_dict_lock[rod+'_'+lock] = 1
            else:
                rode_dict_lock[rod+'_'+lock] += 1
            
            if not rod in rod_dict_lock:
                rod_dict_lock[rod] = 1
            else:
                rod_dict_lock[rod] += 1
        else:
            if not rod+'_'+buff in rode_dict_buff:
                rode_dict_buff[rod+'_'+buff] = 1
            else:
                rode_dict_buff[rod+'_'+buff] += 1

            if not rod in rod_dict_buff:
                rod_dict_buff[rod] = 1
            else:
                rod_dict_buff[rod] += 1

    rode_dict_lock = OrderedDict(sorted(rode_dict_lock.items()))
    rod_dict_lock = OrderedDict(sorted(rod_dict_lock.items()))

    rode_dict_buff = OrderedDict(sorted(rode_dict_buff.items()))
    rod_dict_buff = OrderedDict(sorted(rod_dict_buff.items()))

    for key, value in rod_dict_buff.items():
        if rod_dict_buff[key] < 10:
            del rod_dict_buff[key]
            for key2, val2 in rode_dict_buff.items():
                if key2[:8] == key:
                    del rode_dict_buff[key2]

    for key, value in rod_dict_lock.items():
        if rod_dict_lock[key] < 10:
            del rod_dict_lock[key]
            for key2, val2 in rode_dict_lock.items():
                if key2[:8] == key:
                    del rode_dict_lock[key2]

    for key, value in rod_dict_lock.items():
        print key, value

    #gStyle.SetPalette(kBird)
    #gStyle.SetPalette(kCMYK)
    gStyle.SetPalette(kRainBow)
    TColor.InvertPalette()



    make_plot_all_rods(rode_dict_lock, rod_dict_lock, "all_rods_lock_errors" + sb_suf)
    make_plot_all_rods(rode_dict_buff, rod_dict_buff, "all_rods_buff_errors" + sb_suf)

    if(results[0].sb == 1):
        make_time_rod_evo(rode_dict_lock, rod_dict_lock, results, True)

    make_minute_plots(rod_dict_buff, rod_dict_lock, results)


def make_minute_plots(buff_dict, lock_dict, results):

    hl0 = TH1F('hl0','hl0', 50, 0, 1)
    hl4 = TH1F('hl4','hl4', 50, 0, 1)
    hl8 = TH1F('hl8','hl8', 50, 0, 1)
    hl8.GetXaxis().SetTitle("Fraction of fill length")
    hl8.GetYaxis().SetTitle("Arbitrary units/ 0.02")
    hb0 = TH1F('hb0','h0', 50, 0, 1)
    hb4 = TH1F('hb4','h4', 50, 0, 1)
    hb8 = TH1F('hb8','h8', 50, 0, 1)
    hb8.GetXaxis().SetTitle("Fraction of fill length")
    hb8.GetYaxis().SetTitle("Arbitrary units/ 0.02")

    change_colors_min(hl0, hl4, hl8)
    change_colors_min(hb0, hb4, hb8)


    h0_lock_beg = []
    h0_lock_end = []
    h4_lock_beg = []
    h4_lock_end = []
    h8_lock_beg = []
    h8_lock_end = []

    h0_buff_beg = []
    h0_buff_end = []
    h4_buff_beg = []
    h4_buff_end = []
    h8_buff_beg = []
    h8_buff_end = []

    for r in lock_dict:
        temp0 = TH1F('htl0'+r,'htl0'+r, 80, 0, 240)
        temp1 = TH1F('htl1'+r,'htl1'+r, 80, 0, 240)
        temp2 = TH1F('htl2'+r,'htl2'+r, 96, 0, 480)
        temp3 = TH1F('htl3'+r,'htl3'+r, 96, 0, 480)
        temp4 = TH1F('htl4'+r,'htl4'+r, 180,0, 900)
        temp5 = TH1F('htl5'+r,'htl5'+r, 180,0, 900)
        
        temp0.SetLineWidth(0)
        temp0.SetFillStyle(1001)
        temp1.SetLineWidth(0)
        temp1.SetFillStyle(1001)
        temp2.SetLineWidth(0)
        temp2.SetFillStyle(1001)
        temp3.SetLineWidth(0)
        temp3.SetFillStyle(1001)
        temp4.SetLineWidth(0)
        temp4.SetFillStyle(1001)
        temp5.SetLineWidth(0)
        temp5.SetFillStyle(1001)

        h0_lock_beg.append(temp0)
        h0_lock_end.append(temp1)
        h0_lock_beg[-1].SetDirectory(0)
        h0_lock_end[-1].SetDirectory(0)

        h4_lock_beg.append(temp2)
        h4_lock_end.append(temp3)
        h4_lock_beg[-1].SetDirectory(0)
        h4_lock_end[-1].SetDirectory(0)

        h8_lock_beg.append(temp4)
        h8_lock_end.append(temp5)
        h8_lock_beg[-1].SetDirectory(0)
        h8_lock_end[-1].SetDirectory(0)

    for r in buff_dict:
        temp0 = TH1F('htb0'+r,'htb0'+r, 80, 0, 240)
        temp1 = TH1F('htb1'+r,'htb1'+r, 80, 0, 240)
        temp2 = TH1F('htb2'+r,'htb2'+r, 96, 0, 480)
        temp3 = TH1F('htb3'+r,'htb3'+r, 96, 0, 480)
        temp4 = TH1F('htb4'+r,'htb4'+r, 180,0, 900)
        temp5 = TH1F('htb5'+r,'htb5'+r, 180,0, 900)
        
        temp0.SetLineWidth(0)
        temp0.SetFillStyle(1001)
        temp1.SetLineWidth(0)
        temp1.SetFillStyle(1001)
        temp2.SetLineWidth(0)
        temp2.SetFillStyle(1001)
        temp3.SetLineWidth(0)
        temp3.SetFillStyle(1001)
        temp4.SetLineWidth(0)
        temp4.SetFillStyle(1001)
        temp5.SetLineWidth(0)
        temp5.SetFillStyle(1001)

        h0_buff_beg.append(temp0)
        h0_buff_end.append(temp1)
        h0_buff_beg[-1].SetDirectory(0)
        h0_buff_end[-1].SetDirectory(0)

        h4_buff_beg.append(temp2)
        h4_buff_end.append(temp3)
        h4_buff_beg[-1].SetDirectory(0)
        h4_buff_end[-1].SetDirectory(0)

        h8_buff_beg.append(temp4)
        h8_buff_end.append(temp5)
        h8_buff_beg[-1].SetDirectory(0)
        h8_buff_end[-1].SetDirectory(0)

    for error in results:
        pos_rod  = error.text.find("ROD") + 4
        pos_lock = error.text.find("Lock") + 15
        pos_buff = error.text.find("buffer") + 17

        if error.msgID == 'TRT::ROD05Module':
            rod  = '0x'+str(error.text[pos_rod:pos_rod+6])
        else:
            rod  = str(error.text[pos_rod:pos_rod+8])

        lock = str(error.text[pos_lock:pos_lock+3])
        buff = str(error.text[pos_buff:pos_buff+3])

        for i,key in enumerate(lock_dict):
            if key == rod and lock != '0xf' and error.sb_length > 0.5 and error.sb == 1:
                frac = error.sb_time_run/error.sb_length
                if error.sb_length  < 4:
                    hl0.Fill(frac)
                    h0_lock_beg[i].Fill(error.sb_time_run*60)
                    h0_lock_end[i].Fill(error.sb_length*60 - error.sb_time_run*60)
                elif error.sb_length < 8:
                    hl4.Fill(frac)
                    h4_lock_beg[i].Fill(error.sb_time_run*60)
                    h4_lock_end[i].Fill(error.sb_length*60 - error.sb_time_run*60)
                else:       
                    hl8.Fill(frac) 
                    h8_lock_beg[i].Fill(error.sb_time_run*60)
                    h8_lock_end[i].Fill(error.sb_length*60 - error.sb_time_run*60)
        for i,key2 in enumerate(buff_dict):
           if key2 == rod and buff != '0xf' and error.sb_length > 0.5 and error.sb == 1:
               frac = error.sb_time_run/error.sb_length
               if error.sb_length  < 4:
                   hb0.Fill(frac)
                   h0_buff_beg[i].Fill(error.sb_time_run*60)
                   h0_buff_end[i].Fill(error.sb_length*60 - error.sb_time_run*60)
               elif error.sb_length < 8:
                   hb4.Fill(frac)
                   h4_buff_beg[i].Fill(error.sb_time_run*60)
                   h4_buff_end[i].Fill(error.sb_length*60 - error.sb_time_run*60)
               else:
                   hb8.Fill(frac) 
                   h8_buff_beg[i].Fill(error.sb_time_run*60)
                   h8_buff_end[i].Fill(error.sb_length*60 - error.sb_time_run*60)
    
    leg3 = TLegend(0.23,0.85,0.45,0.75)
    leg3.SetLineColor(0)
    leg3.SetFillStyle(0)
    leg3.SetShadowColor(0)
    leg3.SetBorderSize(0)

    leg3.AddEntry(hl0, "Fill Length: 0-4 hours", "lf")
    leg3.AddEntry(hl4, "Fill Length: 4-8 hours", "lf")
    leg3.AddEntry(hl8, "Fill Length: 8+  hours", "lf")

    c3 = TCanvas( 'c3', 'c3', 1000, 600)
    hl8.DrawNormalized("HIST",1)
    hl0.DrawNormalized("HISTSAME",1)
    hl4.DrawNormalized("HISTSAME",1)
    AtlasStyle.ATLAS_LABEL(0.24,.88, 1, "Internal")
    leg3.Draw()
    AtlasStyle.myText(0.5, 0.88, kBlack, "All RODs: lock errors")
    c3.Update()
    c3.Print("plots/frac_all_lock.pdf")
    c3.Clear()

    hb8.DrawNormalized("HIST",1)
    hb0.DrawNormalized("HISTSAME",1)
    hb4.DrawNormalized("HISTSAME",1)
    AtlasStyle.ATLAS_LABEL(0.24,.88, 1, "Internal")
    leg3.Draw()
    AtlasStyle.myText(0.5, 0.88, kBlack, "All RODs: buffer errors")
    c3.Update()
    c3.Print("plots/frac_all_buff.pdf")
   
    print_single_min(h0_lock_beg, h0_lock_end, "min_lock_0_4", "Lock errors, 0-4 hour fills")
    print_single_min(h4_lock_beg, h4_lock_end, "min_lock_4_8", "Lock errors, 4-8 hour fills")
    print_single_min(h8_lock_beg, h8_lock_end, "min_lock_8",   "Lock errors, 8+  hour fills")
    
    print_single_min(h0_buff_beg, h0_buff_end, "min_buff_0_4", "Buffer errors, 0-4 hour fills")
    print_single_min(h4_buff_beg, h4_buff_end, "min_buff_4_8", "Buffer errors, 4-8 hour fills")
    print_single_min(h8_buff_beg, h8_buff_end, "min_buff_8",   "Buffer errors, 8+  hour fills")

def print_single_min(vec_beg, vec_end, name, text):

    total_beg = vec_beg[0].Clone()
    c = 0
    for v in vec_beg:
        if c != 0:
            total_beg.Add(vec_beg[c])
        c = c + 1
    
    norm = 1/total_beg.Integral()
    total_beg.Scale(norm)

    if 'buff' in name:
        legb = TLegend(0.25,0.93,0.90,0.60)
        legb.SetNColumns(5)
    else:
        legb = TLegend(0.60,0.80,0.90,0.60)
        legb.SetNColumns(2)
    legb.SetLineColor(0)
    legb.SetFillStyle(0)
    legb.SetShadowColor(0)
    legb.SetBorderSize(0)

    if 'buff' in name:
        lege = TLegend(0.25,0.93,0.90,0.60)
        lege.SetNColumns(5)
    else:
        lege = TLegend(0.22,0.90,0.52,0.70)
        lege.SetNColumns(2)
    lege.SetLineColor(0)
    lege.SetFillStyle(0)
    lege.SetShadowColor(0)
    lege.SetBorderSize(0)


    #vec_beg = sorted(vec_beg, key=lambda x: x.Integral(), reverse=True)


    stack1  = THStack("stack1","stack1")
    for v in vec_beg:
        if v.Integral() != 0:
            v.Scale(norm)
            legb.AddEntry(v, v.GetTitle()[4:], "f")
            stack1.Add(v)

    total_end = vec_end[0].Clone()
    c = 0
    for v in vec_end:
        if c != 0:
            total_end.Add(vec_end[c])
        c = c + 1
    
    norm = 1/total_end.Integral()
    total_end.Scale(norm)

    stack2  = THStack("stack2","stack2")
    for v in vec_end:
        if v.Integral() != 0:
            v.Scale(norm)
            lege.AddEntry(v, v.GetTitle()[4:], "f")
            stack2.Add(v)


    total_beg.SetLineColor(kRed)
    total_beg.SetLineWidth(1)
    total_end.SetLineColor(kRed)
    total_end.SetLineWidth(1)

    total_beg.GetXaxis().SetTitle("Minutes after stable beams declared [min]")
    total_end.GetXaxis().SetTitle("Minutes before stable beams ended [min]")

    if '0_4' in name:
        total_beg.GetYaxis().SetTitle("Arbitrary units / 3 mins")
        total_end.GetYaxis().SetTitle("Arbitrary units / 3 mins")
    else:
        total_beg.GetYaxis().SetTitle("Arbitrary units / 5 mins")
        total_end.GetYaxis().SetTitle("Arbitrary units / 5 mins")

    c4 = TCanvas( 'c4', 'c4',1000, 1200)
    c4.Divide(1,2)
    c4.cd(1)
    total_beg.Draw("HIST")
    stack1.Draw("PFC PLC SAME HIST")
    total_beg.Draw("SAMEHIST")
    AtlasStyle.ATLAS_LABEL(0.18,.96, 1, "Internal")
    AtlasStyle.myText(0.40, 0.96, kBlack, text)
    legb.Draw()
    c4.cd(2)
    total_end.Draw("HIST")
    stack2.Draw("PFC PLC SAME HIST")
    total_end.Draw("SAMEHIST")
    AtlasStyle.ATLAS_LABEL(0.18,.96, 1, "Internal")
    AtlasStyle.myText(0.40, 0.96, kBlack, text)
    lege.Draw()
    c4.Update()
    c4.Print("plots/"+name+".pdf")

def change_colors_min(hh1, hh2, hh3):
   
    hh1.SetLineStyle(2)
    hh1.SetLineColor(kCyan-3)
    hh1.SetLineWidth(3)
    
    hh2.SetLineColor(kBlue-8)
    hh2.SetLineWidth(3)
    
    hh3.SetLineColor(kBlack)
    hh3.SetLineWidth(1)
    hh3.SetFillStyle(1001)
    hh3.SetFillColor(kYellow-9)



def make_time_rod_evo(error_dict, rod_dict, results, doLock):
 
    c2 = TCanvas( 'c2', 'c2', 1000, 600)
    leg = TLegend(0.18,0.85,0.45,0.55)
    leg.SetLineColor(0)
    leg.SetFillStyle(0)
    leg.SetShadowColor(0)
    leg.SetBorderSize(0)
    leg.SetNColumns(2)
     
    R15 = TLine(431,0,431,60)
    R15.SetLineColorAlpha(kPink+10,0.4)
    R15.SetLineWidth(4)

    R16 = TLine(1820,0,1820,60)
    R16.SetLineColorAlpha(kMagenta+10,0.4)
    R16.SetLineWidth(4)

    R17 = TLine(3376,0,3376,60)
    R17.SetLineColorAlpha(kGreen-3,0.4)
    R17.SetLineWidth(4)


    TS1 = TLine(431,0,432,60)
    TS1.SetLineColorAlpha(kPink+10,0.5)
    TS1.SetLineWidth(5)

    TS2 = TLine(1415,0,1415,60)
    TS2.SetLineColorAlpha(kMagenta+3,0.5)
    TS2.SetLineWidth(5)

    leg2 = TLegend(0.18,0.45,0.35,0.55)
    leg2.SetLineColor(0)
    leg2.SetFillStyle(0)
    leg2.SetShadowColor(0)
    leg2.SetBorderSize(0)
    gStyle.SetLegendTextSize(0.030)

    leg2.AddEntry(R15, "End of 2015", 'lf')
    leg2.AddEntry(R16, "End of 2016", 'lf')
    leg2.AddEntry(R17, "End of 2017", 'lf')
    #leg2.AddEntry(TS2, "TS2", 'lf')


    for key,val in rod_dict.items(): 
        TS1.SetY2(val*0.5)
        TS2.SetY2(val+1)

        R15.SetY2(val*0.3)
        R16.SetY2(val*0.5)
        R17.SetY2(val*0.8)

        times = {}
        times.clear()
        for e in error_bits:
            times['0x'+e] = [0] 
        for error in results:
            pos_rod  = error.text.find("ROD") + 4
            pos_lock = error.text.find("Lock") + 15
            pos_buff = error.text.find("buffer") + 17

            if error.msgID == 'TRT::ROD05Module':
                rod  = '0x'+str(error.text[pos_rod:pos_rod+6])
            else:
                rod  = str(error.text[pos_rod:pos_rod+8])

            lock = str(error.text[pos_lock:pos_lock+3])
            buff = str(error.text[pos_buff:pos_buff+3])

            if key == rod and doLock and lock != '0xf':
                times[lock].append(error.sb_total_time)


        leg.Clear()
        mg = TMultiGraph()

        for e in error_bits:
            errs = []
            for i,x in enumerate(times['0x'+e]):
                errs.append(i+0.0)
            errs.append(errs[-1])
            #times['0x'+e].append(1800.0)
            times['0x'+e].append(results[-1].sb_total_time)
            gr = TGraph(len(times['0x'+e]), array(times['0x'+e]), array(errs))
            gr.SetMarkerSize(0.7)
            if bin(int('0x'+e, 16))[2:].zfill(4) == '0111':
                leg.AddEntry(gr,'GOL 3',"lp");
            elif bin(int('0x'+e, 16))[2:].zfill(4) == '1011':
                leg.AddEntry(gr,'GOL 2',"lp");
            elif bin(int('0x'+e, 16))[2:].zfill(4) == '1101':
                leg.AddEntry(gr,'GOL 1',"lp");
            elif bin(int('0x'+e, 16))[2:].zfill(4) == '1110':
                leg.AddEntry(gr,'GOL 0',"lp");
            else:
                leg.AddEntry(gr,bin(int('0x'+e, 16))[2:].zfill(4),"lp");
            mg.Add(gr,"pl");

        mg.SetTitle("; Hours of stable beams; # of rocketio io lock errors");
        mg.Draw("PMC PLC a");
        R15.Draw()
        R16.Draw()
        R17.Draw()
        #TS1.Draw()
        #TS2.Draw()
        
        AtlasStyle.ATLAS_LABEL(0.19,.88, 1, "Internal")
        leg.Draw()
        leg2.Draw()
        AtlasStyle.myText(0.4, 0.88, kBlack, "ROD: " + key)
        
        
        leg.SetMargin(0.5)
        gPad.Modified()
        mg.GetXaxis().SetLimits(0,results[-1].sb_total_time)
        mg.SetMinimum(0.)
        mg.SetMaximum(val+1)
        c2.Update()
        c2.Print("plots/time_"+key+".pdf")
        c2.Clear()


def make_plot_all_rods(error_dict, rod_dict, name):
    

    leg = TLegend(0,0,0,0)
    if 'lock' in name:
        leg = TLegend(0.18,0.85,0.50,0.55)
    else:
        leg = TLegend(0.18,0.85,0.40,0.55)
    leg.SetLineColor(0)
    leg.SetFillStyle(0)
    leg.SetShadowColor(0)
    leg.SetBorderSize(0)
    leg.SetNColumns(3)
    gStyle.SetLegendTextSize(0.045)

   
    v_hists = []
    #for e,c in zip(error_bits, error_colors):
    for e in error_bits:
        h = TH1F('h'+e,'h'+e, len(rod_dict), 0, len(rod_dict))
        h.SetFillStyle(1001)
        h.SetLineWidth(0)
        v_hists.append(h)
        v_hists[-1].SetDirectory(0)
        if bin(int('0x'+e, 16))[2:].zfill(4) == '0111':
            leg.AddEntry(v_hists[-1],'GOL 3',"f");
        elif bin(int('0x'+e, 16))[2:].zfill(4) == '1011':
            leg.AddEntry(v_hists[-1],'GOL 2',"f");
        elif bin(int('0x'+e, 16))[2:].zfill(4) == '1101':
            leg.AddEntry(v_hists[-1],'GOL 1',"f");
        elif bin(int('0x'+e, 16))[2:].zfill(4) == '1110':
            leg.AddEntry(v_hists[-1],'GOL 0',"f");
        else:
            leg.AddEntry(v_hists[-1],bin(int('0x'+e, 16))[2:].zfill(4),"f");
    h = leg.GetY2()-leg.GetY1();
    w = leg.GetX2()-leg.GetX1()*.6;
    leg.SetMargin(leg.GetNColumns()*h/(leg.GetNRows()*w))
    

    for key,val in error_dict.items():
        idx_rod = 0
        for i, key2 in enumerate(rod_dict):
            if key2 == key[:8]:
                idx_rod = i
        v_hists[int(key[11:12], 16)].Fill(idx_rod, val)
  
    stack  = THStack("stack","stack")
    for hist in v_hists:
        stack.Add(hist)

    if 'buff' in name:
        c1 = TCanvas( 'c1', 'c1', 2000, 500)
    else:
        c1 = TCanvas( 'c1', 'c1', 1000, 500)


    h1 = TH1F('h_1','h_1', len(rod_dict), 0, len(rod_dict))
    for i, key in enumerate(rod_dict):
        h1.GetXaxis().SetBinLabel(i+1,key)
        h1.SetBinContent(i+1,rod_dict[key])

 
    h1.GetXaxis().LabelsOption("v")
    h1.GetXaxis().SetTitle("ROD")
    h1.GetXaxis().SetTitleOffset(2.2)
    h1.GetYaxis().SetTitle("# of rocketio errors")
    h1.SetLineColor(kRed)
    h1.SetLineWidth(1)

    leg.AddEntry(h1,'total',"l");
    
    c1.SetBottomMargin(0.23)  
    h1.GetXaxis().SetTitle("ROD")
    h1.Draw("HIST")
    stack.Draw("PFC PLC SAME HIST")
    h1.Draw("SAMEHIST")
    AtlasStyle.ATLAS_LABEL(0.19,.88, 1, "Internal")
    leg.Draw()
    c1.Update()
    c1.Print("plots/"+name +".pdf")
    c1.Clear()


if __name__ == '__main__':
    main()
