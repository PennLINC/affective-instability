# ==============================================================================
# Script: anonymize_outputs.R
# Description: 
#   This script processes and anonymizes GGIR output files for actigraphy data.
#   It performs the following operations:
#   1. Reads GGIR output CSV files from subject directories (part2, part4, part5)
#   2. Adds month and year columns to the data
#   3. Standardizes participant IDs to ensure they start with "sub-" prefix
#   4. Reorganizes files into a BIDS-like directory structure: 
#      sub-<ID>/actigraphy/
#   5. Converts CSV files to TSV format
#   6. Renames files with standardized naming convention:
#      sub-<ID>_level-<day|night|person>[_thresh-<threshold>]_desc-<deviceinfo|sleep|activity>_actigraphy.tsv
#   7. Processes config.csv files and converts them to config.tsv
#
# Input: 
#   - GGIR output files in base_dir (default: <root>/ggir_output/)
#   - Files processed: part2_summary.csv, part2_daysummary.csv, 
#     part4_nightsummary_sleep_cleaned.csv, part4_summary_sleep_cleaned.csv,
#     part5_daysummary_MM_L40M100V400_T5A5.csv, part5_personsummary_MM_L40M100V400_T5A5.csv
#
# Output:
#   - Ready-to-release TSV files in output_dir (default: <root>/releases/release_<today's date>/ggir/)
#   - Organized by subject: sub-<ID>/actigraphy/
# ==============================================================================

library(tidyverse)
library(lubridate)
library(janitor)

# Set root directory
root <- "/Volumes/pafin/sourcedata/actigraphy/derivatives"

# Set base directory
base_dir <- file.path(root, "ggir_all_outputs")

# Set output directory
output_dir <- file.path(root, "ggir")

# List of files to process
file_names <- c(
  "part2_summary.csv",
  "part2_daysummary.csv",
  "part4_nightsummary_sleep_cleaned.csv",
  "part4_summary_sleep_cleaned.csv",
  "part5_daysummary_MM_L40M100V400_T5A5.csv",
  "part5_personsummary_MM_L40M100V400_T5A5.csv"
)

# Function to process a single file
process_file <- function(file_path, file_name) {
  if (!file.exists(file_path)) return(NULL)
  df <- read_csv(file_path, show_col_types = FALSE) %>% 
    janitor::clean_names(case = "snake")
  
  # Find the date column: prefer calendar_date, else start_date
  if ("calendar_date" %in% names(df)) {
    date_col <- "calendar_date"
    date_vec <- df[[date_col]]
    # If calendar_date is not already Date, try to parse
    if (!inherits(date_vec, "Date")) {
      date_vec <- as.Date(date_vec)
    }
    month_val <- month(date_vec, label = TRUE, abbr = TRUE)
    year_val <- year(date_vec)
  } else if ("start_time" %in% names(df)) {
    date_col <- "start_time"
    # Parse start_date as datetime
    date_vec <- ymd_hms(str_sub(df[[date_col]], 1, 19))
    month_val <- month(date_vec, label = TRUE, abbr = TRUE)
    year_val <- year(date_vec)
  } else {
    warning(paste("No calendar_date or start_time column found in", file_path))
    return(NULL)
  }
  
  # Add month and year, keeping date_col
  df <- df %>%
    mutate(
      month = month_val,
      year = year_val
    )
  
  # Build column order: id, optional columns, month, year, date_col, then everything else
  col_order <- c("id")
  if ("night" %in% names(df)) col_order <- c(col_order, "night")
  if ("window_number" %in% names(df)) col_order <- c(col_order, "window_number")
  if ("measurementday" %in% names(df)) col_order <- c(col_order, "measurementday")
  if ("weekday" %in% names(df)) col_order <- c(col_order, "weekday")
  if ("startday" %in% names(df)) col_order <- c(col_order, "startday")
  col_order <- c(col_order, "month", "year", date_col)
  remaining_cols <- setdiff(names(df), col_order)
  col_order <- c(col_order, remaining_cols)
  
  df <- df %>%
    select(all_of(col_order)) # window_number means day in part5_daysummary_MM_L40M100V400_T5A5.csv
  
  # Ensure participant_id starts with sub- if present
  if ("id" %in% names(df)) {
    df <- df %>%
      mutate(id = ifelse(
        !str_starts(id, "sub-"),
        paste0("sub-", id),
        id
      )) %>%
      rename(participant_id = id)
  }
  
  # Rename columns for part4_summary and part2_summary files
  if (str_detect(file_name, "part4_summary") | str_detect(file_name, "part2_summary")) {
    df <- df %>%
      rename(
        start_weekday = any_of(c("weekday", "startday")),
        start_month = month,
        start_year = year
      )
  }
  
  return(df)
}

# Main loop over subject directories
subject_dirs <- list.dirs(base_dir, recursive = FALSE, full.names = TRUE)

# Check for missing CSV files for each subject
cat("\n=== Checking for required CSV files ===\n")
subjects_with_all_files <- character(0)
subjects_with_missing_files <- character(0)

for (subject_dir in subject_dirs) {
  subject_folder <- basename(subject_dir)
  subject_id <- str_remove(subject_folder, "^output_")
  results_dir <- file.path(subject_dir, "results")
  
  # Check if each required file exists
  missing_files <- character(0)
  for (file_name in file_names) {
    file_path <- file.path(results_dir, file_name)
    if (!file.exists(file_path)) {
      missing_files <- c(missing_files, file_name)
    }
  }
  
  if (length(missing_files) == 0) {
    subjects_with_all_files <- c(subjects_with_all_files, subject_id)
  } else {
    subjects_with_missing_files <- c(subjects_with_missing_files, subject_id)
    cat("Subject", subject_id, "missing files:", paste(missing_files, collapse = ", "), "\n")
  }
}

# Print summary
cat("\n=== Summary ===\n")
if (length(subjects_with_missing_files) == 0) {
  cat("All subjects had all required result files.\n")
} else {
  cat("Subjects with all files:", length(subjects_with_all_files), "\n")
  cat("Subjects with missing files:", length(subjects_with_missing_files), "\n")
  cat("Subject IDs with missing files:", paste(subjects_with_missing_files, collapse = ", "), "\n")
}
cat("\n=== Processing files ===\n")

total_subjects <- length(subject_dirs)
files_processed <- 0

for (subject_dir in subject_dirs) {
  subject_folder <- basename(subject_dir)
  # Extract subject ID and build new folder name
  subject_id <- str_remove(subject_folder, "^output_")
  subject_label <- paste0("sub-", subject_id)
  
  cat("Processing subject:", subject_id, "\n")
  
  # Set up the corresponding output directory (sub-<ID>/actigraphy)
  output_results_dir <- file.path(output_dir, subject_label, "actigraphy")
  dir.create(output_results_dir, recursive = TRUE, showWarnings = FALSE)
  
  results_dir <- file.path(subject_dir, "results")
  
  for (file_name in file_names) {
    file_path <- file.path(results_dir, file_name)
    
    # Determine level, desc, and thresh to build output filename
    if (str_detect(file_name, "day")) {
      level <- "day"
    } else if (str_detect(file_name, "night")) {
      level <- "night"
    } else {
      level <- "person"
    }
    # Determine desc and thresh
    if (str_detect(file_name, "part2")) {
      desc <- "deviceinfo"
      thresh <- NULL
    } else if (str_detect(file_name, "part4")) {
      desc <- "sleep"
      thresh <- NULL
    } else if (str_detect(file_name, "part5")) {
      desc <- "activity"
      # Extract threshold string (e.g., L40M100V400) from filename
      thresh_match <- str_match(file_name, "L\\d+M\\d+V\\d+")
      thresh <- if (!is.na(thresh_match[1])) paste0("_thresh-", thresh_match[1]) else ""
    } else {
      desc <- "unknown"
      thresh <- NULL
    }
    # Compose new filename
    if (!is.null(thresh) && thresh != "") {
      new_filename <- paste0(subject_label, "_level-", level, thresh, "_desc-", desc, "_actigraphy.tsv")
    } else {
      new_filename <- paste0(subject_label, "_level-", level, "_desc-", desc, "_actigraphy.tsv")
    }
    out_path <- file.path(output_results_dir, new_filename)
    
    # Check if output file already exists
    if (file.exists(out_path)) {
      cat("  Output file already exists, skipping:", new_filename, "\n")
      next
    }
    
    processed_df <- process_file(file_path, file_name)
    if (!is.null(processed_df)) {
      write_tsv(processed_df, out_path, na = "n/a")
      files_processed <- files_processed + 1
    }
  }
}

# Copy and convert config.csv to config.tsv for each subject
cat("\n=== Processing config files ===\n")
config_count <- 0
for (subject_dir in subject_dirs) {
  subject_folder <- basename(subject_dir)
  subject_id <- str_remove(subject_folder, "^output_")
  subject_label <- paste0("sub-", subject_id)
  config_csv <- file.path(subject_dir, "config.csv")
  # Place config.tsv in sub-<ID>/actigraphy/
  config_tsv_out <- file.path(output_dir, subject_label, "actigraphy", paste0(subject_label, "_config.tsv"))
  
  # Check if output file already exists
  if (file.exists(config_tsv_out)) {
    cat("  Config file already exists, skipping:", basename(config_tsv_out), "\n")
    next
  }
  
  if (file.exists(config_csv)) {
    config_df <- read_csv(config_csv, show_col_types = FALSE)
    write_tsv(config_df, config_tsv_out, na = "n/a")
    config_count <- config_count + 1
  }
}

# Print completion messages
cat("\n=== Processing Complete ===\n")
cat("✓ Processed", total_subjects, "subjects\n")
cat("✓ Output directory:", output_dir, "\n")
cat("\nAll files have been successfully anonymized and saved!\n")

# add print for missing files
cat("\n=== Missing files ===\n")
cat("Subjects with missing files:", paste(subjects_with_missing_files, collapse = ", "), "\n")
# print these subjects may have insufficient activity data
cat("These subjects may have insufficient actigraphy data\n")