library(GGIR)

# this script has been modified from the original ggir_process.R script shareed by Nathalia Esper
# to run on PAFin data, which currently does not have sleep logs. Modifications all concern part 4 and include:
# 1) removing sleeplog and cleaning log arguments
# 2) setting relyonguider to FALSE because there are no guider-based sleep logs
# 3) removing sleeplogidnum and sleeplogsep as they concern sleep logs


# Get command-line arguments
args <- commandArgs(trailingOnly = TRUE)
subjectID <- args[1]
raw_data_dir_path <- args[2]  # Raw data directory
output_dir_path <- args[3]  # Output directory
# sleeplog_path <- args[4]  # Sleep log path
# cleaning_log_path <- args[5]  # Cleaning log path

GGIR(#=======================================
             # INPUT NEEDED:
            mode=c(1,2,3,4,5),
            datadir=raw_data_dir_path,
            outputdir=output_dir_path,
            studyname=subjectID, 
            f0=0, f1=c(),
            overwrite = TRUE,
            idloc=6,
            print.filename=TRUE,
            storefolderstructure = FALSE,
            dformat=2,
            mon=3,
            do.parallel=FALSE,
            #-------------------------------
            # Part 1:
            #-------------------------------
            desiredtz = "America/New_York",
            do.enmo = TRUE,
            do.anglez=TRUE,
            do.hfen = FALSE,
            windowsizes = c(5,900,3600),
            do.cal=TRUE,
            chunksize=1,
	        printsummary=TRUE,
            #-------------------------------
            # Part 2:
            #-------------------------------
            strategy = 1,
            hrs.del.start = 0,
            hrs.del.end = 0,
            maxdur = 0,
            #includedaycrit = 16, # for midnight-midnight (this was already commented out in the original script)
            winhr = c(5,10),
            epochvalues2csv=TRUE,
            L5M5window = c(0,24),
            M5L5res = 10,
            qlevels = c(c(1380/1440),c(1410/1440)),
            qwindow=c(0,24),
            ilevels = c(seq(0,400,by=50),8000),
            mvpathreshold =c(125),
            do.imp=TRUE,
            #-------------------------------
            # Part 3:
            # (detection of sustained inactivity periods as needed for sleep detection in g.part4)
            #-------------------------------
            timethreshold= c(5),
            anglethreshold = 5,
            ignorenonwear = TRUE,
            nonwear_approach = "2023",
            #-------------------------------
	        # Part 4:
            # （Labels detected sustained inactivity periods by g.part3 as either nocturnal sleep or daytime sustained inactivity)
            #-------------------------------
            excludefirstlast = FALSE,
            includenightcrit = 12,
            def.noc.sleep = c(1),
            # loglocation = sleeplog_path,  # optional guider-based sleep onset and offset 
            colid = 1,
            coln1 = 2,
            # sleeplogsep = ",",
            # data_cleaning_file = cleaning_log_path, # optional, guider-based nights to exclude 
            outliers.only = FALSE,
            relyonguider = FALSE, # set to TRUE if have sleeplogs
            # sleeplogidnum = TRUE,
            do.visual = TRUE,
            do.sibreport = TRUE,
            criterror = 0,
            #-------------------------------
            # Part 5:
            #-------------------------------
            threshold.lig = c(30,40,50),
            threshold.mod = c(100,120,125),
            threshold.vig = c(400,500),
            boutcriter = 0.8,
            boutcriter.in = 0.9,
            boutcriter.lig = 0.8,
            boutcriter.mvpa = 0.8,
            boutdur.in = c(10,20,30),
            boutdur.lig = c(1,5, 10),
            boutdur.mvpa = c(1,5,10),
            timewindow = c("WW", "MM"),
            # -----------------------------------
            # Report generation
            # -----------------------------------
            do.report=c(2,4,5),
            visualreport=TRUE,
            dofirstpage = TRUE,
            viewingwindow=2
  )
