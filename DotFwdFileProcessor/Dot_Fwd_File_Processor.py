# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DotFwdFileProcessor
                                 A QGIS plugin
 This plugin processes .fwd files to polyline for web mapping use
                              -------------------
        begin                : 2017-01-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Eric Kabuchanga | Senior Developer | KEGeoS Solutions Limited
        email                : kabuchanga@kegeos.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from os.path import expanduser
# Initialize Qt resources from file resources.py
import resources, re
# Import the code for the dialog
from Dot_Fwd_File_Processor_dialog import DotFwdFileProcessorDialog
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.utils import iface
import os.path
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

x = QSettings()
oldValidation = x.value( "/Projections/defaultBehaviour")
x.setValue( "/Projections/defaultBehaviour", "useGlobal" )


class DotFwdFileProcessor:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DotFwdFileProcessor_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = DotFwdFileProcessorDialog()       


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&DotFwdFileProcessor')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DotFwdFileProcessor')
        self.toolbar.setObjectName(u'DotFwdFileProcessor')

        self.dlg.listWidget.clear()
        self.dlg.pushButton_4.clicked.connect(self.select_output_files)

        self.dlg.lineEdit_4.clear()
        self.dlg.pushButton_3.clicked.connect(self.select_input_dir)

        self.dlg.lineEdit_3.clear()
        self.dlg.pushButton_2.clicked.connect(self.select_output_file)

        self.dlg.lineEdit_2.clear()
        self.dlg.pushButton.clicked.connect(self.select_input_file)



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DotFwdFileProcessor', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/DotFwdFileProcessor/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ProcessDotFWD'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&DotFwdFileProcessor'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_input_dir(self):
        my_dir = QFileDialog.getExistingDirectory(self.dlg, "Select Folder", expanduser("~"), QFileDialog.ShowDirsOnly)
        self.dlg.lineEdit_4.setText(my_dir)

    def select_output_files(self):
        fdlg = QFileDialog()
        my_dir = fdlg.getExistingDirectory(self.dlg, "Select Folder", expanduser("~"), fdlg.ShowDirsOnly)
        self.dlg.lineEdit_5.setText(my_dir)
        self.dlg.listWidget.clear()
        self.dlg.listWidget_2.clear()
        for file in os.listdir(my_dir):
            if file.endswith(".fwd") or file.endswith(".FWD") :
                csvfile = file.strip(".fwd")
                self.dlg.listWidget.addItem(file)
                self.dlg.listWidget_2.addItem(csvfile.strip(".FWD") + ".csv")
        self.dlg.listWidget_2.show()
        self.dlg.listWidget_2.show()

    def select_output_dir(self):
        my_dir = QFileDialog.getExistingDirectory(self.dlg, "Select Folder", expanduser("~"), QFileDialog.ShowDirsOnly)
        self.dlg.lineEdit_5.setText(my_dir)

    def select_input_file(self):
        filename = QFileDialog.getOpenFileName(self.dlg, "Select FWD file", "",'*.fwd')
        self.dlg.lineEdit_2.setText(filename)

    def select_output_file(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file", "",'*.csv')
        self.dlg.lineEdit_3.setText(filename)

    def dms2dd(self, degrees, minutes, seconds, direction):
        dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
        #if direction == 'E' or direction == 'N':
        if direction == 'S' or direction == 'W':
            dd *= -1
        return dd;

    def error_log(self, err_msg):
        home = expanduser("~")
        print  home
        file_path =  os.path.join(home + "\Desktop", "error_log.txt")
        print  file_path
        if os.path.exists(file_path):
            wrt_tofle = open(file_path, "a")
            wrt_tofle.write(err_msg + "\n")
            wrt_tofle.close()
        else:
            wrt_tofle = open(file_path, "w")
            #wrt_tofle.open(file_path, "a")
            wrt_tofle.write(err_msg + "\n")
            wrt_tofle.close()

    def dd2dms(self, deg):
        d = int(deg)
        md = abs(deg - d) * 60
        m = int(md)
        sd = (md - m) * 60
        return [d, m, sd]

    def parse_dms(self,dms):
        parts = dms.split("m") #re.split('m', dms)#re.split('[^\d\w\.]+', dms) #re.split('[^\d\w]+', dms)
        lat = self.dms2dd(parts[0], parts[1], parts[2], parts[3])
        return (lat)

    def parse_dms2(self,dms):
        parts = dms.split("m") #re.split('m', dms)#re.split('[^\d\w\.]+', dms) #re.split('[^\d\w]+', dms)
        dg=parts[0]
        mint = dg[-2:]
        dirc = dg[:1]
        lat = self.dms2dd(dg[1:-3], mint, parts[1], dirc)
        return (lat)

    def eqpmnt(self):
        radios=["eqpt1","eqpt2"]
        qpname=""
        for i in range(0,2):
            selected_radio = self.dlg.findChild(QRadioButton, radios[i])
            if selected_radio.isChecked():
                qpname = selected_radio.objectName()
                print selected_radio.objectName() + "is Checked"
        return qpname
    def proceqpmnt_1(self, in_fwdfilename, main_csvfilename):
        #print "fx called"
        #write the csv file header
        outputfile = open(main_csvfilename, 'w')
        #print "file opened"
        outputfile.write('Road_Name, Road_ID,County,Chainage, Lane,Pavement_type,Remarks, Longitude,Latitude,Altitude,D1,D2,D3,D4,D5,D6,D7,D8,D9,Pressure, Load, Air_Temp, Surface_Temp, Pavement_Temp,Pulse_Time \n')
        #print "header writen"
        Chainage = "a00200"
        Longitude = "222"
        Latitude = "222"
        Road_Name, Road_ID, County, Lane, Pavement_type, Remarks, Altitude, D1, D2, D3, D4, D5, D6, D7, D8, D9, Pressure, Load, Air_Temp, Surface_Temp, Pavement_Temp, Pulse_Time = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        dflcts1, dflcts2  = [],[]
        D9 = "10000"
        varx = 1
        #print "variables intialized"
        varf = 0
        filNme = ""
        for line in open(in_fwdfilename) :
            try:
                if "Road reference" in line:
                    rdnm = line.split("Road reference:........")
                    rd = rdnm[1]
                    Road_Name = rd.lstrip()
                    filNme = Road_Name
                if "Road number" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Road number:...........")
                    rd =rdnm[1]
                    Road_ID = rd.lstrip()

                if "Districtnumber" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Districtnumber:........")
                    rd =rdnm[1]
                    County = rd.lstrip()

                if "Lane" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Lane...................")
                    rd =rdnm[1]
                    Lane = rd.lstrip()

                if "Pavement description" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Pavement description...")
                    rd =rdnm[1]
                    Pavement_type = rd.lstrip()

                if "Remarks" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Remarks................")
                    rd =rdnm[1]
                    Remarks = ""#rd.lstrip()

                if "Chainage" in line:
                    lin = line.rstrip('\n')
                    chng = lin.split("Chainage [m]...........")
                    Chainage = chng[1]

                if "Position of Drop" in line:
                    #newline = line.rstrip('\n')
                    loc = line.rstrip('\n')
                    lon = loc.split(":")
                    lona = lon[2]
                    print lona
                    lon2=lona.split('	')
                    j= lon2[0]
                    q=j.replace("\"", "m")
                    s = q.decode('utf-8')
                    t=s.rstrip('\n')
                    r=t.replace("'", "m")
                    q=r.replace("\"", "m")
                    p=r.replace("°", "m")
                    print p
                    Longitude = self.parse_dms(p)
                    print(Longitude)

                if "Position of Drop" in line:
                    #newline = line.rstrip('\n')
                    loc = line.rstrip('\n')
                    lon = loc.split(":")
                    lata = lon[3]
                    lat2=lata.split('	')
                    j= lat2[0]
                    print j
                    q=j.replace("\"", "m")
                    s = q.decode('utf-8')
                    t=s.rstrip('\n')
                    r=t.replace("'", "m")
                    p=r.replace("°", "m")
                    print p
                    Latitude =   self.parse_dms(p)
                    #print(Latitude)
                if "Position of Drop" in line:
                    #newline = line.rstrip('\n')
                    loc = line.rstrip('\n')
                    lon = loc.split(":")
                    alta = lon[4]
                    alt2=alta.split(' ')
                    j= alt2[1]
                    print j
                    s = j.decode('utf-8')
                    Altitude = s
                    print(Altitude)

                if line.startswith('1'):
                    wrknline = line.rstrip('\n')
                    #dflcts1 = [""] * 20
                    dflcts1 = wrknline.split('	')
                if line.startswith('2'):
                    wrknline = line.rstrip('\n')
                    #dflcts2 = [""] * 20
                    dflcts2 = wrknline.split('	')
                print len(dflcts1)
                print dflcts1
                if "$2" in line:
                    print len(dflcts1)
                    print dflcts1
                    if (len(dflcts1) > 0 and len(dflcts2) > 0):
                        Air_Temp= str((float(dflcts1[12]) + float(dflcts2[12]))/2)
                        Surface_Temp=str((float(dflcts1[13]) + float(dflcts2[13]))/2)
                        Pavement_Temp=str((float(dflcts1[14]) + float(dflcts2[14]))/2)
                        Pressure=str((float(dflcts1[10]) + float(dflcts2[10]))/2)
                        D1=str((float(dflcts1[1]) + float(dflcts2[1]))/2)
                        D2=str((float(dflcts1[2]) + float(dflcts2[2]))/2)
                        D3=str((float(dflcts1[3]) + float(dflcts2[3]))/2)
                        D4=str((float(dflcts1[4]) + float(dflcts2[4]))/2)
                        D5=str((float(dflcts1[5]) + float(dflcts2[5]))/2)
                        D6=str((float(dflcts1[6]) + float(dflcts2[6]))/2)
                        D7=str((float(dflcts1[7]) + float(dflcts2[7]))/2)
                        D8=str((float(dflcts1[8]) + float(dflcts2[8]))/2)
                        D9=str((float(dflcts1[9]) + float(dflcts2[9]))/2)
                        Load = str((float(dflcts1[11]) + float(dflcts2[11])) / 2)
                        Pulse_Time = str((float(dflcts1[15]) + float(dflcts2[15])) / 2)

                    elif len(dflcts1) == 0 and len(dflcts1)== 0:
                        var22 = 24
                    elif len(dflcts1) == 0 and len(dflcts2)> 0:
                        print "Tests true"
                        Air_Temp= str(dflcts2[12])
                        Surface_Temp =str(dflcts2[13])
                        Pavement_Temp=str(dflcts2[14])
                        Pressure=str(dflcts2[10])
                        D1=str(dflcts2[1])
                        print "Two " + dflcts1[1]
                        print dflcts2[1]
                        print D1
                        D2=str(dflcts2[2])
                        D3=str(dflcts2[3])
                        D4=str(dflcts2[4])
                        D5=str(dflcts2[5])
                        D6=str(dflcts2[6])
                        D7=str(dflcts2[7])
                        D8=str(dflcts2[8])
                        D9=str(dflcts2[9])
                        Load = str(dflcts2[11])
                        Pulse_Time = str(dflcts2[15])

                    elif len(dflcts2) == 0 and len(dflcts1)> 0:
                        Air_Temp= str(dflcts1[12])
                        Surface_Temp=str(dflcts1[13])
                        Pavement_Temp=str(dflcts1[14])
                        Pressure=str(dflcts1[10])
                        D1=str(dflcts1[1])
                        print "three " + dflcts1[1]
                        print dflcts1[1]
                        print D1
                        D2=str(dflcts1[2])
                        D3=str(dflcts1[3])
                        D4=str(dflcts1[4])
                        D5=str(dflcts1[5])
                        D6=str(dflcts1[6])
                        D7=str(dflcts1[7])
                        D8=str(dflcts1[8])
                        D9=str(dflcts1[9])
                        Load = str(dflcts1[11])
                        Pulse_Time = str(dflcts1[15])
                    else:
                        print "badline"

                if (Chainage !="a00200" and Longitude !="222" and Latitude !="222" and D9 != "10000"):
                    print ("xlon " + Chainage.rstrip('\n')+ "," + str(Longitude) +',' + str(Latitude))
                    print len("Df One "+ str(dflcts1[1]))
                    print len("DF Two "+ str(dflcts2[1]))
                    newline = Road_Name.rstrip('\n') + ','+ Road_ID.rstrip('\n') + ',' +  County.rstrip('\n')+ ','+ Chainage.rstrip('\n') + ','+ Lane.rstrip('\n')+ ','+ Pavement_type.rstrip('\n')+ ','+ Remarks.rstrip('\n')+ "," + str(Longitude) +',' + str(Latitude) + ',' + Altitude.rstrip('\n') + ','+ D1+ ','+ D2+ ','+ D3+ ','+ D4+ ','+ D5 + ','+ D6 + ','+ D7 + ','+ D8 + ','+ D9 + ',' + Pressure + ','+ Load + ',' + Air_Temp + ',' + Surface_Temp + ',' + Pavement_Temp + ',' + Pulse_Time
                    outputfile.write(newline.rstrip('\n') + '\n')
                    varx =varx+1
                    if varx == 6:
                        varg=5
                        #break
                    del dflcts1[:]
                    del dflcts2[:]
                    Chainage = "a00200"
                    Longitude = "222"
                    Latitude = "222"
                    D9 = "10000"
                if "$2" in line:
                    del dflcts1[:]
                    del dflcts2[:]
                    Chainage = "a00200"
                    Longitude = "222"
                    Latitude = "222"
                    D9 = "10000"
                #Altitude, Air_Temp, Surface_Temp_Temp, Pavement_Temp, Pressure, D1, D2, D3,D4,D5, D6, D7, D8, D9
                #outputfile.write(line.rstrip('\n')) # .rstrip('\n') removes the line break
                varf = varf + 1
            except Exception as e:
                self.error_log("________________________________________________________________________________________________ \n File Name: " + filNme + " has error at Chainage; " + Chainage.strip('\n') + " on line; " + str(varf + 1) + "\n" + e.__str__())
        outputfile.close()
        del outputfile
        print "Done!"
        return filNme

    def proceqpmnt_2(self, in_fwdfilename, main_csvfilename):
        #print "fx called"
        #write the csv file header
        outputfile = open(main_csvfilename, 'w')
        #print "file opened"
        outputfile.write('Road_Name, Road_ID,County,Chainage,Lane,Pavement_type,Remarks,Longitude,Latitude,Altitude,D1,D2,D3,D4,D5,D6,D7,D8,D9,Pressure,Load,Air_Temp,Surface_Temp,Pavement_Temp,Pulse_Time \n')
        #print "header writen"
        Chainage = "a00200"
        Longitude = "222"
        Latitude = "222"
        Road_Name, Road_ID, County, Lane, Pavement_type, Remarks, Altitude, D1, D2, D3, D4, D5, D6, D7, D8, D9, Pressure, Load, Air_Temp, Surface_Temp, Pavement_Temp, Pulse_Time = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        dflcts1, dflcts2  = [],[]
        D9 = "10000"
        varx = 1
        #print "variables intialized"
        vark = 0
        filName = ""
        for line in open(in_fwdfilename) :
            try:
                if "Filename" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Filename:..............")
                    rd =rdnm[1]
                    Road_Name = rd.lstrip()
                    filName = Road_Name
                if "Road number" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Road number:...........")
                    rd =rdnm[1]
                    Road_ID = rd.lstrip()

                if "Districtnumber" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Districtnumber:........")
                    rd =rdnm[1]
                    County = rd.lstrip()

                if "Lane" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Lane...................")
                    rd =rdnm[1]
                    Lane = rd.lstrip()

                if "Pavement description" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Pavement description...")
                    rd =rdnm[1]
                    Pavement_type = rd.lstrip()

                if "Remarks" in line:
                    line.rstrip('\n')
                    rdnm = line.split("Remarks................")
                    rd =rdnm[1]
                    Remarks = ""#rd.lstrip()

                if "Chainage" in line:
                    lin = line.rstrip('\n')
                    chng = lin.split("Chainage[m]............")
                    Chainage = chng[1]

                if "Position of Drop" in line:
                    #newline = line.rstrip('\n')
                    loc = line.rstrip('\n')
                    lon = loc.split(":")
                    lona = lon[2]
                    lon2_a = lona.rstrip(" ")
                    lon2 = lon2_a.split(',')
                    kkt= lon2[0]
                    j= kkt.replace("East","E")
                    q=j.replace("\"", "m")
                    s = q.rstrip(" ") #q.decode('utf-8')
                    PYTHONIOENCODING="UTF-8"
                    t=s#.decode('utf-8')
                    r=t.replace("'", "m")
                    q=r.replace("\"", "m")
                    p=r.replace(" ","")#replace("°", "m")
                    Longitude = self.parse_dms2(p)
                    #print(Longitude)

                if "Position of Drop" in line:
                    #newline = line.rstrip('\n')
                    loc = line.rstrip('\n')
                    lon = loc.split(":")
                    lona = lon[3]
                    lon2_a = lona.rstrip(" ")
                    lon2 = lon2_a.split(',')
                    kkt= lon2[0]
                    j= kkt.replace("South","S")
                    q=j.replace("\"", "m")
                    s = q.rstrip(" ") #q.decode('utf-8')
                    PYTHONIOENCODING="UTF-8"
                    t=s#.decode('utf-8')
                    r=t.replace("'", "m")
                    q=r.replace("\"", "m")
                    p=r.replace(" ","")#replace("°", "m")
                    Latitude =   self.parse_dms2(p)
                    #print(Latitude)

                if "Position of Drop" in line:
                    #newline = line.rstrip('\n')
                    loc = line.rstrip('\n')
                    lon = loc.split(":")
                    alta = lon[4]
                    alt2=alta.split(' ')
                    j= alt2[1]
                    s = j.decode('utf-8')
                    Altitude = s
                    print(Altitude)

                if line.startswith('1'):
                    wrknline = line.rstrip('\n')
                    #dflcts1 = [""] * 20
                    dflcts1 = wrknline.split('	')
                if line.startswith('2'):
                    wrknline = line.rstrip('\n')
                    #dflcts1 = [""] * 20
                    dflcts2 = wrknline.split('	')
                print len(dflcts1)
                print dflcts1
                if "$2" in line:
                    print len(dflcts1)
                    print dflcts1
                    if (len(dflcts1) > 0 and len(dflcts2) > 0):
                        Air_Temp= str((float(dflcts1[12]) + float(dflcts2[12]))/2)
                        Surface_Temp=str((float(dflcts1[13]) + float(dflcts2[13]))/2)
                        Pavement_Temp=str((float(dflcts1[14]) + float(dflcts2[14]))/2)
                        Pressure=str((float(dflcts1[10]) + float(dflcts2[10]))/2)
                        D1=str((float(dflcts1[1]) + float(dflcts2[1]))/2)
                        D2=str((float(dflcts1[2]) + float(dflcts2[2]))/2)
                        D3=str((float(dflcts1[3]) + float(dflcts2[3]))/2)
                        D4=str((float(dflcts1[4]) + float(dflcts2[4]))/2)
                        D5=str((float(dflcts1[5]) + float(dflcts2[5]))/2)
                        D6=str((float(dflcts1[6]) + float(dflcts2[6]))/2)
                        D7=str((float(dflcts1[7]) + float(dflcts2[7]))/2)
                        D8=str((float(dflcts1[8]) + float(dflcts2[8]))/2)
                        D9=str((float(dflcts1[9]) + float(dflcts2[9]))/2)
                        Load = str((float(dflcts1[11]) + float(dflcts2[11])) / 2)
                        Pulse_Time = str((float(dflcts1[15]) + float(dflcts2[15])) / 2)

                    elif len(dflcts1) == 0 and len(dflcts1)== 0:
                        var22 = 24
                    elif len(dflcts1) == 0 and len(dflcts2)> 0:
                        print "Tests true"
                        Air_Temp= str(dflcts2[12])
                        Surface_Temp=str(dflcts2[13])
                        Pavement_Temp=str(dflcts2[14])
                        Pressure=str(dflcts2[10])
                        D1=str(dflcts2[1])
                        print "Two " + dflcts1[1]
                        print dflcts2[1]
                        print D1
                        D2=str(dflcts2[2])
                        D3=str(dflcts2[3])
                        D4=str(dflcts2[4])
                        D5=str(dflcts2[5])
                        D6=str(dflcts2[6])
                        D7=str(dflcts2[7])
                        D8=str(dflcts2[8])
                        D9=str(dflcts2[9])
                        Load = str(dflcts2[11])
                        Pulse_Time = str(dflcts2[15])

                    elif len(dflcts2) == 0 and len(dflcts1)> 0:
                        Air_Temp= str(dflcts1[12])
                        Surface_Temp=str(dflcts1[13])
                        Pavement_Temp=str(dflcts1[14])
                        Pressure=str(dflcts1[10])
                        D1=str(dflcts1[1])
                        print "three " + dflcts1[1]
                        print dflcts1[1]
                        print D1
                        D2=str(dflcts1[2])
                        D3=str(dflcts1[3])
                        D4=str(dflcts1[4])
                        D5=str(dflcts1[5])
                        D6=str(dflcts1[6])
                        D7=str(dflcts1[7])
                        D8=str(dflcts1[8])
                        D9=str(dflcts1[9])
                        Load = str(dflcts1[11])
                        Pulse_Time = str(dflcts1[15])
                    else:
                        print "badline"

                if (Chainage !="a00200" and Longitude !="222" and Latitude !="222" and D9 != "10000"):
                    print ("xlon " + Chainage.rstrip('\n')+ "," + str(Longitude) +',' + str(Latitude))
                    print len("Df One "+ str(dflcts1[1]))
                    print len("DF Two "+ str(dflcts2[1]))
                    newline = Road_Name.rstrip('\n') + ','+ Road_ID.rstrip('\n') + ',' + County.rstrip('\n')+ ','+ Chainage.rstrip('\n') + ','+ Lane.rstrip('\n')+ ','+ Pavement_type.rstrip('\n')+ ','+ Remarks.rstrip('\n')+ "," + str(Longitude) +',' + str(Latitude) + ',' + Altitude.rstrip('\n') + ','+ D1+ ','+ D2+ ','+ D3+ ','+ D4+ ','+ D5 + ','+ D6 + ','+ D7 + ','+ D8 + ','+ D9 + ',' + Pressure + ','+ Load + ',' + Air_Temp + ',' + Surface_Temp + ',' + Pavement_Temp + ',' + Pulse_Time
                    outputfile.write(newline.rstrip('\n') + '\n')
                    varx =varx+1
                    if varx == 6:
                        varg=5
                        #break
                    del dflcts1[:]
                    del dflcts2[:]
                    Chainage = "a00200"
                    Longitude = "222"
                    Latitude = "222"
                    D9 = "10000"
                if "$2" in line:
                    del dflcts1[:]
                    del dflcts2[:]
                    Chainage = "a00200"
                    Longitude = "222"
                    Latitude = "222"
                    D9 = "10000"
                #Altitude, Air_Temp, Surface_Temp, Pavement_Temp, Pressure, D1, D2, D3,D4,D5, D6, D7, D8, D9
                #outputfile.write(line.rstrip('\n')) # .rstrip('\n') removes the line break
                vark = vark + 1
            except Exception as e:
                self.error_log("________________________________________________________________________________________________ \n File Name: " + filName + " has error at Chainage; " + Chainage.strip('\n') + " on line; " + str(vark + 1)+ "\n" + e.__str__())
        outputfile.close()
        del outputfile
        print "Done!"
        return filName.strip(".fwd")

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        RoadID, RouteName = "",""
        if result:
            currentIndex = self.dlg.tabWidget.currentIndex()
            currentWidget = self.dlg.tabWidget.currentWidget()
            processingMode = "Single"
            if self.eqpmnt()=="eqpt1":
                print 'Query: current Tab is '+ str(currentIndex)
                if currentIndex == 0:
                    #implementation single processing
                    fwd_filename = self.dlg.lineEdit_2.text()
                    kkk = open(fwd_filename, 'a')
                    kkk.write("$2  ")
                    kkk.close()
                    del kkk
                    del fwd_filename
                    fwdfilename = self.dlg.lineEdit_2.text()
                    csvfilename = self.dlg.lineEdit_3.text()
                    print self.eqpmnt()
                    lyrName = self.proceqpmnt_1(fwdfilename, csvfilename)

                    InFlPth = "file:///" + csvfilename
                    uri = InFlPth + "?crs=epsg:4326&delimiter=%s&xField=%s&yField=%s" % (",", "Longitude", "Latitude")
                    bh = QgsVectorLayer(uri, lyrName, "delimitedtext")
                    bh.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                    QgsMapLayerRegistry.instance().addMapLayer(bh)
                    # self.x.setValue( "/Projections/defaultBehaviour", oldValidation )
                else:
                    #implementation batch processing
                    btchProc = "Batch Processing"
                    print btchProc
                    Mycsv_fildir = self.dlg.lineEdit_4.text()
                    Myfwd_fildir = self.dlg.lineEdit_5.text()
                    rdId = 0
                    for file in os.listdir(Myfwd_fildir):
                        if file.endswith(".fwd") or file.endswith(".FWD"):
                            csvfile = file.strip(".fwd")
                            fwd_filename = os.path.join(Myfwd_fildir , file)
                            kkk = open(fwd_filename, 'a')
                            kkk.write("$2  ")
                            kkk.close()
                            del kkk
                            del fwd_filename
                            fwdfilename = os.path.join(Myfwd_fildir , file)
                            csvfilename = os.path.join(Mycsv_fildir, csvfile.strip(".FWD") + ".csv")
                            lyrName = self.proceqpmnt_1(fwdfilename, csvfilename)

                            InFlPth = "file:///" + csvfilename
                            uri = InFlPth + "?crs=epsg:4326&delimiter=%s&xField=%s&yField=%s" % (
                            ",", "Longitude", "Latitude")
                            bh = QgsVectorLayer(uri, lyrName, "delimitedtext")
                            bh.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                            QgsMapLayerRegistry.instance().addMapLayer(bh)

            elif self.eqpmnt() == "eqpt2":
                if currentIndex == 0:
                    #implementation single processing
                    fwd_filename = self.dlg.lineEdit_2.text()
                    kkk = open(fwd_filename, 'a')
                    kkk.write("$2  ")
                    kkk.close()
                    del kkk
                    del fwd_filename
                    fwdfilename = self.dlg.lineEdit_2.text()
                    csvfilename = self.dlg.lineEdit_3.text()
                    print self.eqpmnt()
                    layrNme = self.proceqpmnt_2(fwdfilename, csvfilename)
                    InFlPth = "file:///" + csvfilename
                    uri = InFlPth + "?crs=epsg:4326&delimiter=%s&xField=%s&yField=%s" % (",", "Longitude", "Latitude")
                    bh = QgsVectorLayer(uri, layrNme, "delimitedtext")
                    bh.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                    QgsMapLayerRegistry.instance().addMapLayer(bh)
                        # self.x.setValue( "/Projections/defaultBehaviour", oldValidation )
                else:
                    #implementation batch processing
                    btchProc="Batch Processing"
                    print btchProc
                    Mycsv_fildir = self.dlg.lineEdit_4.text()
                    Myfwd_fildir = self.dlg.lineEdit_5.text()
                    rdId = 0
                    for file in os.listdir(Myfwd_fildir):
                        if file.endswith(".fwd") or file.endswith(".FWD"):
                            csvfile = file.strip(".fwd")
                            fwd_filename = os.path.join(Myfwd_fildir, file)
                            kkk = open(fwd_filename, 'a')
                            kkk.write("$2  ")
                            kkk.close()
                            del kkk
                            del fwd_filename
                            fwdfilename = os.path.join(Myfwd_fildir, file)
                            csvfilename = os.path.join(Mycsv_fildir, csvfile.strip(".FWD") + ".csv")
                            lyrName = self.proceqpmnt_2(fwdfilename, csvfilename)
                            InFlPth = "file:///" + csvfilename
                            uri = InFlPth + "?crs=epsg:4326&delimiter=%s&xField=%s&yField=%s" % (
                                ",", "Longitude", "Latitude")
                            bh = QgsVectorLayer(uri, lyrName, "delimitedtext")
                            bh.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                            QgsMapLayerRegistry.instance().addMapLayer(bh)

            else:
                thingIs = "equipment not known"
                print (thingIs)

            # Do something useful here - delete the line containing pass and
            # substitute with your code.

            pass
