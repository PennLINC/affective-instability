# wrapper_run_ggir.R
# This script is a wrapper for the GGIR script that processes the raw data and outputs the results to a specified directory.

# Define root directory
root_dir <- "/Volumes/pafin"
# path to code
code_dir <- "/Users/joelleba/PennLINC/pafin/code/ggir"
setwd(root_dir)

# find all .bin files recursively in geneactiv_raw_data
raw_data_base <- file.path(root_dir, "sourcedata", "actigraphy", "sourcedata", "raw")
bin_files <- list.files(raw_data_base, pattern = "\\.bin$", recursive = TRUE, full.names = TRUE)

if (length(bin_files) == 0) {
  stop("No .bin files found in ", raw_data_base)
}

# Extract subject IDs from filenames (remove path and .bin extension)
subject_list <- gsub("\\..*$", "", basename(bin_files))
cat("Found", length(subject_list), "subjects with raw data\n")
# Create a named vector to map subject IDs to their full file paths
subject_paths <- setNames(bin_files, subject_list)

# Loop through each subject and call the GGIR script
for (subject in subject_list) {
  cat("Running GGIR for subject:", subject, "\n")
  
  # Get the full path to the .bin file (may be in a subdirectory)
  raw_data_dir_path <- subject_paths[subject]
  output_dir_path <- file.path(root_dir, "sourcedata", "actigraphy", "derivatives", "ggir_all_outputs")
  
  # sleeplog_path = paste0("./sleeplogs/processed_sleeplog_", subject, ".csv")
  # cleaning_log_path = paste0("./sleeplogs/data_cleaning_", subject, ".csv")

  # create output directory if it doesn't exist
  if (!dir.exists(output_dir_path)) {
    dir.create(output_dir_path)
  }
  
  # Check if subject has already been processed
  subject_output_dir <- file.path(output_dir_path, paste0("output_", subject))
  subject_results_dir <- file.path(subject_output_dir, "results")
  
  if (dir.exists(subject_output_dir) && dir.exists(subject_results_dir)) {
    # Check if results directory contains files (indicating processing completed)
    result_files <- list.files(subject_results_dir, pattern = "\\.csv$", full.names = FALSE)
    if (length(result_files) > 0) {
      cat("Subject", subject, "has already been processed. Skipping.\n")
      cat("Found", length(result_files), "result file(s) in", subject_results_dir, "\n")
      next
    }
  }
  
  # print input and output paths
  cat("Raw data file:", raw_data_dir_path, "\n")
  cat("Output directory:", output_dir_path, "\n")
  # cat("Sleep log file:", sleeplog_path, "\n")
  # cat("Cleaning log file:", cleaning_log_path, "\n")

  # run GGIR for the subject
  # Find Rscript path
  rscript_path <- Sys.which("Rscript")
  if (rscript_path == "") {
    # If not in PATH, try to find it in R's bin directory
    rscript_path <- file.path(R.home("bin"), "Rscript")
    if (!file.exists(rscript_path)) {
      stop("Could not find Rscript. Please ensure R is properly installed.")
    }
  }
  
  # Construct command with full path to Rscript
  script_path <- file.path(code_dir, "ggir_process_pafin.R")
  command <- paste(
    shQuote(rscript_path),
    shQuote(script_path),
    shQuote(subject),
    shQuote(raw_data_dir_path),
    shQuote(output_dir_path),
    sep = " "
  )
  cat("Command:", command, "\n")
  system(command)
  cat("Finished processing subject:", subject, "\n")
}

# Check that all input subjects were successfully processed
cat("\n=== Verifying processing completion ===\n")
output_dir_path <- file.path(root_dir, "sourcedata", "actigraphy", "derivatives", "ggir_all_outputs")
unique_subjects <- unique(subject_list)
subjects_with_output <- character(0)
subjects_missing_output <- character(0)

for (subject in unique_subjects) {
  subject_output_dir <- file.path(output_dir_path, paste0("output_", subject))
  subject_results_dir <- file.path(subject_output_dir, "results")
  
  if (dir.exists(subject_output_dir) && dir.exists(subject_results_dir)) {
    result_files <- list.files(subject_results_dir, pattern = "\\.csv$", full.names = FALSE)
    if (length(result_files) > 0) {
      subjects_with_output <- c(subjects_with_output, subject)
    } else {
      subjects_missing_output <- c(subjects_missing_output, subject)
      cat("Subject", subject, "has output directory but no result files\n")
    }
  } else {
    subjects_missing_output <- c(subjects_missing_output, subject)
    cat("Subject", subject, "missing output directory or results folder\n")
  }
}

# Print summary
cat("\n=== Processing Verification Summary ===\n")
cat("Total input subjects:", length(unique_subjects), "\n")
cat("Subjects with successful outputs:", length(subjects_with_output), "\n")
cat("Subjects missing outputs:", length(subjects_missing_output), "\n")

if (length(subjects_missing_output) == 0) {
  cat("\n✓ All subjects were successfully processed!\n")
} else {
  cat("\n✗ Subjects missing outputs:", paste(subjects_missing_output, collapse = ", "), "\n")
}
