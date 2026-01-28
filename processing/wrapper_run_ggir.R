# wrapper_run_ggir.R
# This script is a wrapper for the GGIR script that processes the raw data and outputs the results to a specified directory.

# Define root directory
root_dir <- "/Users/joelleba/Documents/large_data/pafin"
# path to code
code_dir <- "/Users/joelleba/PennLINC/pafin/code/ggir"
setwd(root_dir)

# find subject IDs in root_dir + /raw_data
subject_list <- list.files(file.path("./geneactiv_raw_data"))
subject_list <- gsub("\\..*", "", subject_list)

# Loop through each subject and call the GGIR script
for (subject in subject_list) {
  cat("Running GGIR for subject:", subject, "\n")
  
  raw_data_dir_path = paste0("./geneactiv_raw_data/", subject, ".bin")
  output_dir_path = paste0("./ggir_output")
  # sleeplog_path = paste0("./sleeplogs/processed_sleeplog_", subject, ".csv")
  # cleaning_log_path = paste0("./sleeplogs/data_cleaning_", subject, ".csv")

  # create output directory if it doesn't exist
  if (!dir.exists(output_dir_path)) {
    dir.create(output_dir_path)
  }
  
  # print input and output paths
  cat("Raw data file:", raw_data_dir_path, "\n")
  cat("Output directory:", output_dir_path, "\n")
  # cat("Sleep log file:", sleeplog_path, "\n")
  # cat("Cleaning log file:", cleaning_log_path, "\n")

  # run GGIR for the subject
  command <- paste(
    "Rscript ggir_process_pafin.R", 
    subject,
    raw_data_dir_path,
    output_dir_path,
    # sleeplog_path,
    # cleaning_log_path
  )
  system(command)
  cat("Finished processing subject:", subject, "\n")
}



