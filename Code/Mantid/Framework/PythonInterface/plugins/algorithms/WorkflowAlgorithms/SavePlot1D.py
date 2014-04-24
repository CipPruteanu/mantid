"""*WIKI* 

Save 1D plots to a png file, as part of autoreduction.

*WIKI*"""
import mantid
 
class SavePlot1D(mantid.api.PythonAlgorithm):

    def category(self):
	""" Category
	"""
        return "Utilities;PythonAlgorithms"

    def name(self):
	""" Algorithm name
	"""
        return "SavePlot1D"
    
    def checkGroups(self):
        return False
        
    def PyInit(self):
        self.setWikiSummary("Save 1D plots to a file")
        #declare properties
        self.declareProperty(mantid.api.WorkspaceProperty("InputWorkspace","",mantid.kernel.Direction.Input),"Workspace to plot")
        self.declareProperty(mantid.api.FileProperty('OutputFilename', '', action=mantid.api.FileAction.Save, extensions = ["png"]), doc='Name of the image file to savefile.')
        self.declareProperty("XLabel","","Label on the X axis. If empty, it will be taken from workspace")
        self.declareProperty("YLabel","","Label on the Y axis. If empty, it will be taken from workspace")
			

    def PyExec(self):
        self._wksp = self.getProperty("InputWorkspace").value
        plt.figure()
        if type(self._wksp)==mantid.api._api.WorkspaceGroup:
            for i in range(self._wksp.getNumberOfEntries()):
                plt.subplot(self._wksp.getNumberOfEntries(),1,i+1)
                self.DoPlot(self._wksp.getItem(i))
        else:
            self.DoPlot(self._wksp) 
        plt.tight_layout(1.08)
        plt.show()
        filename = self.getProperty("OutputFilename").value
        plt.savefig(filename,bbox_inches='tight')    
        
    def DoPlot(self,ws):
        spectra=ws.getNumberHistograms()
        if spectra>10:
            mantid.kernel.logger.warning("more than 10 spectra to plot")
        prog_reporter=mantid.api.Progress(self,start=0.0,end=1.0,
                    nreports=spectra)
        
        for j in range(spectra):
            x=ws.readX(j)
            y=ws.readY(j)
            if x.size==y.size+1:
                x=(x[:-1]+x[1:])*0.5  
            #get labels for the curves
            a=ws.getAxis(1)
            if a.isSpectra():
                plotlabel=a.label(j)
            else:
                plotlabel=unicode(a.title())+" = "+str(float(a.label(j)))   
            plt.plot(x,y,label=plotlabel)
            xlabel=self.getProperty("XLabel").value
            ylabel=self.getProperty("YLabel").value
            if xlabel=="":
                xaxis=ws.getAxis(0)
                unitLabel=xaxis.getUnit().symbol().utf8()
                if unitLabel=='1/Angstrom' or unitLabel=='Angstrom^-1':
                    unitLabel="$\\AA^{-1}$"
                if unitLabel=='Angstrom':
                    unitLabel="$\\AA$"   
                xlabel=xaxis.getUnit().caption()+" ("+unitLabel+")"
            if ylabel=="":
                ylabel=ws.YUnit()              

            plt.xlabel(xlabel)
            plt.ylabel(ylabel) 
            prog_reporter.report("Processing") 
        if spectra>1 and spectra<=10:            
            plt.legend()
                   
        
try:
    import matplotlib
    matplotlib.use("agg")
    import matplotlib.pyplot as plt
    mantid.api.AlgorithmFactory.subscribe(SavePlot1D)
except:
    mantid.kernel.logger.debug('Failed to subscribe algorithm SavePlot1D; Python package matplotlib may be missing')
    pass
