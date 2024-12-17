# This code was built from work by Jean-Yves Tinevez, for which I am very grateful!
# Sources include:
# https://imagej.net/plugins/trackmate/scripting/scripting
# https://imagej.net/plugins/trackmate/scripting/trackmate-detectors-trackers-keys
# https://github.com/trackmate-sc/TrackMate-Cellpose

# This script analyses a directory of tiff files (single channel 2D timelapses from mammary gland intravital imaging) using a detection model trained in Cellpose 2.2.2 to detect cell shape, track this over time and export shape measurements.
# It is assumed that you already have a trained Cellpose model, either the MaSCOT-AI model or your own.

# This script automates the processing of a directory of single channel 2D timelapse movies using the TrackMate plugin in Fiji/ImageJ. It performs the following tasks:
# Configures directories for input images, saved tracks, models, and feature statistics.
# Iterates through each file in the specified directory, loading them into ImageJ and running TrackMate with the specified model and configurations.
# Logs the number of tracks found and outputs track and spot features (e.g., position, size, intensity) for each detected track and its associated spots.
# Exports cells features including ellipse aspect ratio, solidity and circularity into CSV files.
# Exports XML files, including both a detailed model file and a tracks-only file.

# Directories need to be specified for images, export, Cellpose model, Cellpose python installation

# Required software/packages
# ImageJ 1.54h
# Plugins: Trackmate 7.11.1
# Miniconda
# Cellpose Conda environment with Cellpose 2.2.2 installation (and additional packages listed here: https://pypi.org/project/cellpose/)
# Conda pytorch install for GPU processing

import sys

from ij import IJ
from ij import WindowManager

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.tracking.jaqaman import SimpleSparseLAPTrackerFactory
from fiji.plugin.trackmate.tracking.jaqaman import SparseLAPTrackerFactory
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettings
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
from fiji.plugin.trackmate.cellpose import CellposeDetectorFactory
from  fiji.plugin.trackmate.cellpose.CellposeSettings import PretrainedModel
from fiji.plugin.trackmate.io import TmXmlWriter
import fiji.plugin.trackmate.action.ExportTracksToXML as ExportTracksToXML
from fiji.plugin.trackmate.visualization.table import TrackTableView
from fiji.plugin.trackmate.visualization.table import AllSpotsTableView
from fiji.plugin.trackmate.visualization.trackscheme import TrackScheme
from fiji.plugin.trackmate.gui.displaysettings.DisplaySettings import TrackMateObject
from fiji.plugin.trackmate.gui.displaysettings.DisplaySettings import TrackDisplayMode


# We have to do the following to avoid errors with UTF8 chars generated in 
# TrackMate that will mess with our Fiji Jython.
reload(sys)
sys.setdefaultencoding('utf-8')

# Import required libraries
import os
from java.io import File

# Define the directories
directory = ".../Max projections/"
trackSaveDirectory = ".../exportTracks"
modelSaveDirectory = ".../exportModels"
tracksDirectory = ".../trackStats"
spotsDirectory = ".../spotStats"

# Loop through each file in the directory
for filename in os.listdir(directory):
    # Check if the file is an image
    #if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        # Open the image
        imp = IJ.openImage(os.path.join(directory, filename))
        
        #----------------------------
        # Create the model object now
        #----------------------------

        # Some of the parameters we configure below need to have
        # a reference to the model at creation. So we create an
        # empty model now.

        model = Model()

        # Send all messages to ImageJ log window.
        model.setLogger(Logger.IJ_LOGGER)

        #------------------------
        # Prepare settings object
        #------------------------

        settings = Settings(imp)

        # Configure detector - We use the Strings for the keys
        settings.detectorFactory = CellposeDetectorFactory()
        settings.detectorSettings = {
            'TARGET_CHANNEL' : 0,
            'OPTIONAL_CHANNEL_2' : 0,
            'CELLPOSE_PYTHON_FILEPATH' : '...\Miniconda3\envs\cellpose\python.exe',
            'CELLPOSE_MODEL' : PretrainedModel.CUSTOM,
            'CELLPOSE_MODEL_FILEPATH' : '...\CellposeModel',
            'CELL_DIAMETER' : 0.,
                   #0. will automatically determine diameter
            'USE_GPU' : True,
            'SIMPLIFY_CONTOURS' : False,
        }  

        # Configure spot filters - Classical filter on quality
        filter1 = FeatureFilter('AREA', 250, False)
        settings.addSpotFilter(filter1)

        # Configure tracker - We want to allow merges and fusions
        settings.trackerFactory = SparseLAPTrackerFactory()
        settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
        settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
        settings.trackerSettings['ALLOW_TRACK_MERGING'] = False

        #set sparseLAPTracker settings
        settings.trackerFactory = SparseLAPTrackerFactory()
        settings.trackerSettings = settings.trackerFactory.getDefaultSettings()
        settings.trackerSettings['LINKING_MAX_DISTANCE'] = 3.
        settings.trackerSettings['MAX_FRAME_GAP'] = 3
        settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 5.

        # Add ALL the feature analyzers known to TrackMate. They will 
        # yield numerical features for the results, such as speed, mean intensity etc.
        settings.addAllAnalyzers()

        #penalise differences in size (weak) and intensity (strong) - only for not simple
        penalty = {
            'AREA' : 5.,
            'MEAN_INTENSITY_CH1' : 5.
        }

        # Configure track filters - We only want tracks with 3 or more timepoints

        filter2 = FeatureFilter('TRACK_DURATION', 3, True)
        settings.addTrackFilter(filter2)


        #filter2 = FeatureFilter('TRACK_ID',is_empty(), False)
        #settings.addTrackFilter(filter2)

        #-------------------
        # Instantiate plugin
        #-------------------

        trackmate = TrackMate(model, settings)

        #--------
        # Process
        #--------

        ok = trackmate.checkInput()
        if not ok:
            sys.exit(str(trackmate.getErrorMessage()))

        ok = trackmate.process()
        if not ok:
            sys.exit(str(trackmate.getErrorMessage()))


        #----------------
        # Display results
        #----------------

        model.getLogger().log('Found ' + str(model.getTrackModel().nTracks(True)) + ' tracks.')

        # A selection.
        sm = SelectionModel( model )

        # Read the default display settings.
        ds = DisplaySettingsIO.readUserDefault()

        # The viewer.
        displayer =  HyperStackDisplayer( model, sm, imp, ds ) 
        displayer.render()

        # The feature model, that stores edge and track features.
        fm = model.getFeatureModel()

        # Iterate over all the tracks that are visible.
        for id in model.getTrackModel().trackIDs(True):

            # Fetch the track feature from the feature model.
            v = fm.getTrackFeature(id, 'TRACK_DURATION')
            model.getLogger().log('')
            model.getLogger().log('Track ' + str(id) + ': duration = ' + str(v) + model.getTimeUnits())

        	# Get all the spots of the current track.
            track = model.getTrackModel().trackSpots(id)
            for spot in track:
                sid = spot.ID()
                # Fetch spot features directly from spot.
                # Note that for spots the feature values are not stored in the FeatureModel
                # object, but in the Spot object directly. This is an exception; for tracks
                # and edges, you have to query the feature model.
                x=spot.getFeature('POSITION_X')
                y=spot.getFeature('POSITION_Y')
                t=spot.getFeature('FRAME')
                snr=spot.getFeature('SNR_CH1')
                q=spot.getFeature('QUALITY')
                mean=spot.getFeature('MEAN_INTENSITY_CH1')
                c=spot.getFeature('CIRCULARITY')
                e=spot.getFeature('ELLIPSE_ASPECTRATIO')
                a=spot.getFeature('AREA')
                model.getLogger().log('\tspot ID = ' + str(sid) + ': c='+str(c)+', e='+str(e)+', a='+str(a)+', x='+str(x)+', y='+str(y)+', t='+str(t)+', q='+str(q) + ', snr='+str(snr) + ', mean = ' + str(mean))


	    # Specify the paths for the spots and tracks files
        baseName = os.path.splitext(filename)[0]
        savePathSpots = os.path.join(spotsDirectory, baseName + "_spots.csv")
        savePathTracks = os.path.join(tracksDirectory, baseName + "_tracks.csv")

        # Create File objects
        csvFileSpots = File(savePathSpots)
        csvFileTracks = File(savePathTracks)

        # Your original function
        trackTableView = TrackTableView(trackmate.getModel(), sm, ds)
        trackTableView.getSpotTable().exportToCsv(csvFileSpots)
        trackTableView.getTrackTable().exportToCsv(csvFileTracks)
	    
	    
	    #something to do with updating settings so that xml exports properly
	    
        from fiji.plugin.trackmate.providers import SpotAnalyzerProvider
        from fiji.plugin.trackmate.providers import EdgeAnalyzerProvider
        from fiji.plugin.trackmate.providers import TrackAnalyzerProvider

        # Compute edge properties, following https://github.com/fiji/TrackMate/issues/120
        settings.clearSpotAnalyzerFactories()
        #spotAnalyzerProvider = SpotAnalyzerProvider()
        spotAnalyzerProvider    = SpotAnalyzerProvider(imp.getNChannels())
        spotAnalyzerKeys = spotAnalyzerProvider.getKeys()
        for key in spotAnalyzerKeys:
            spotFeatureAnalyzer = spotAnalyzerProvider.getFactory(key)
            settings.addSpotAnalyzerFactory(spotFeatureAnalyzer)

        settings.clearEdgeAnalyzers()
        edgeAnalyzerProvider = EdgeAnalyzerProvider()
        edgeAnalyzerKeys = edgeAnalyzerProvider.getKeys()
        for key in edgeAnalyzerKeys:
            edgeAnalyzer = edgeAnalyzerProvider.getFactory(key)
            settings.addEdgeAnalyzer(edgeAnalyzer)

        settings.clearTrackAnalyzers();
        trackAnalyzerProvider = TrackAnalyzerProvider()
        trackAnalyzerKeys = trackAnalyzerProvider.getKeys()
        for key in trackAnalyzerKeys:
            trackAnalyzer = trackAnalyzerProvider.getFactory(key)
            settings.addTrackAnalyzer(trackAnalyzer)
        
        ##to write the xml files in the same folder
        #path and filename are the names of the folder and file where you want to save
        baseName = os.path.splitext(filename)[0]
        
        outFile = File(trackSaveDirectory, baseName+"_exportTracks.xml")   #this will write the tracks only XML
        ExportTracksToXML.export(model, settings, outFile)
        outFile = File(modelSaveDirectory, baseName+"_exportModel.xml")  # this will write the full trackmate xml.
        writer = TmXmlWriter(outFile) 
        writer.appendModel(model)
        writer.appendSettings(settings)
        writer.writeToFile()
        
        
        imp.close()
