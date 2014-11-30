#################################################################################################
# Background Data Updater
#################################################################################################

import xbmc
import xbmcgui
import xbmcaddon

import json
import threading
from datetime import datetime
import urllib
from DownloadUtils import DownloadUtils
from Database import Database

_MODE_BASICPLAY=12

#define our global download utils
downloadUtils = DownloadUtils()
db = Database()

class BackgroundDataUpdaterThread(threading.Thread):

    logLevel = 2
    
    def __init__(self, *args):
        addonSettings = xbmcaddon.Addon(id='plugin.video.xbmb3c')
        level = addonSettings.getSetting('logLevel')        
        self.logLevel = 2
        if(level != None):
            self.logLevel = int(level)           
        self.logLevel = 2
        xbmc.log("XBMB3C BackgroundDataUpdaterThread -> Log Level:" +  str(self.logLevel))
        
        threading.Thread.__init__(self, *args)    
    
    def logMsg(self, msg, level = 1):
        if(self.logLevel >= level):
            xbmc.log("XBMB3C BackgroundDataUpdaterThread -> " + msg)
                
    def run(self):
        self.logMsg("Started")
        
        self.updateBackgroundData()
        lastRun = datetime.today()
        lastProfilePath = xbmc.translatePath('special://profile')
        
        while (xbmc.abortRequested == False):
            td = datetime.today() - lastRun
            secTotal = td.seconds
            
            profilePath = xbmc.translatePath('special://profile')
            
            updateInterval = 60
            if (xbmc.Player().isPlaying()):
                updateInterval = 300
                
            if(secTotal > updateInterval or lastProfilePath != profilePath):
                self.updateBackgroundData()
                lastRun = datetime.today()

            lastProfilePath = profilePath
            
            xbmc.sleep(3000)
                        
        self.logMsg("Exited")
        
    def updateBackgroundData(self):
        self.logMsg("updateBackgroundData Called")
        db.set("itemString","")
        addonSettings = xbmcaddon.Addon(id='plugin.video.xbmb3c')
        mb3Host = addonSettings.getSetting('ipaddress')
        mb3Port = addonSettings.getSetting('port')    
        userName = addonSettings.getSetting('username')     
        
        userid = downloadUtils.getUserId()
        
        self.logMsg("UserName : " + userName + " UserID : " + userid)
        
        self.logMsg("Updating BackgroundData Movie List")
        WINDOW = xbmcgui.Window( 10000 )
        dataUrl = "http://" + mb3Host + ":" + mb3Port + "/mediabrowser/Users/" + userid + "/Items?Recursive=true&SortBy=SortName&Fields=Path,Genres,MediaStreams,Overview,ShortOverview,CriticRatingSummary&SortOrder=Ascending&Filters=IsUnplayed,IsNotFolder&IncludeItemTypes=Movie&format=json"
         
        jsonData = downloadUtils.downloadUrl(dataUrl, suppress=False, popup=1 )
        result = json.loads(jsonData)
        self.logMsg("BackgroundData Movie Json Data : " + str(result), level=2)
        
        result = result.get("Items")
        if(result == None):
            result = []
        item_count = 1
        for item in result:
            title = "Missing Title"
            if(item.get("Name") != None):
                title = item.get("Name").encode('utf-8')
            
            rating = item.get("CommunityRating")
            criticrating = item.get("CriticRating")
            officialrating = item.get("OfficialRating")
            criticratingsummary = ""
            if(item.get("CriticRatingSummary") != None):
                criticratingsummary = item.get("CriticRatingSummary").encode('utf-8')
            plot = item.get("Overview")
            if plot == None:
                plot=''
            plot=plot.encode('utf-8')
            shortplot = item.get("ShortOverview")
            if shortplot == None:
                shortplot = ''
            shortplot = shortplot.encode('utf-8')
            if(item.get("RunTimeTicks") != None):
                runtime = str(int(item.get("RunTimeTicks"))/(10000000*60))
            else:
                runtime = "0"

            url =  mb3Host + ":" + mb3Port + ',;' + item.get("Id")
            playUrl = "plugin://plugin.video.xbmb3c/?url=" + url + '&mode=' + str(_MODE_BASICPLAY)
            playUrl = playUrl.replace("\\\\","smb://")
            playUrl = playUrl.replace("\\","/")    
            self.updateDB(item)
            
    def updateDB(self, item):
        id=item.get("Id")
        itemString=db.get("itemString")
        if itemString=='':
            itemString=id
        else:
            itemString=itemString + "," +id
        db.set("itemString", itemString)
        Temp = item.get("Name")
        if Temp == None:
            Temp = ""
        Name=Temp.encode('utf-8')
        db.set(id+".Name",Name)
        Temp = item.get("Overview")
        if Temp == None:
            Temp=''
        Overview1=Temp.encode('utf-8')
        Overview=str(Overview1)
        db.set(id+".Overview",Overview)
        db.set(id+".OfficialRating",item.get("OfficialRating"))
        CommunityRating=item.get("CommunityRating")
        if CommunityRating != None:
            db.set(id+".CommunityRating",       str(CommunityRating))
        db.set(id+".CriticRating",              str(item.get("CriticRating")))
        db.set(id+".ProductionYear",            str(item.get("ProductionYear")))
        db.set(id+".LocationType",              item.get("LocationType"))
        db.set(id+".Primary",                   downloadUtils.getArtwork(item, "Primary")) ,
        db.set(id+".Backdrop",                  downloadUtils.getArtwork(item, "Backdrop")) ,
        db.set(id+".poster",                    downloadUtils.getArtwork(item, "poster")) , 
        db.set(id+".tvshow.poster",             downloadUtils.getArtwork(item, "tvshow.poster")) ,
        db.set(id+".Banner",                    downloadUtils.getArtwork(item, "Banner")) ,
        db.set(id+".Logo",                      downloadUtils.getArtwork(item, "Logo")) ,
        db.set(id+".Disc",                      downloadUtils.getArtwork(item, "Disc")) ,
        db.set(id+".Art",                       downloadUtils.getArtwork(item, "Art")) ,
        db.set(id+".Thumb",                     downloadUtils.getArtwork(item, "Thumb")) ,
        db.set(id+".Thumb3",                    downloadUtils.getArtwork(item, "Thumb3")) ,
        db.set(id+".Primary2",                  downloadUtils.getArtwork(item, "Primary2")) ,
        db.set(id+".Primary4",                  downloadUtils.getArtwork(item, "Primary4")) ,
        db.set(id+".Primary3",                  downloadUtils.getArtwork(item, "Primary3")) ,
        db.set(id+".Backdrop2",                 downloadUtils.getArtwork(item, "Backdrop2")) ,
        db.set(id+".Backdrop3",                 downloadUtils.getArtwork(item, "Backdrop3")) ,
        db.set(id+".BackdropNoIndicators",      downloadUtils.getArtwork(item, "BackdropNoIndicators"))                  
