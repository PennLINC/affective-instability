library(tidyverse)
library(lubridate)
library(janitor)

# Set root directory
root <- "/Users/joelleba/Documents/large_data/pafin/"

# Set base directory
base_dir <- paste0(root, "ggir_output")

# Set output directory
output_dir <- paste0(root, "anonymized_ggir_output")

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
  
  # Add month and year, then drop date_col
  df <- df %>%
    mutate(
      month = month_val,
      year = year_val
    ) %>%
    select(id, any_of(c("night", "window_number", "measurementday")), 
        any_of(c("weekday", "startday")), month, year, everything(), 
        -all_of(date_col), -contains("date")) # window_number means day in part5_daysummary_MM_L40M100V400_T5A5.csv
  
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

  # remove start_time column if it exists
  if ("start_time" %in% names(df)) {
    df <- df %>% select(-start_time)
  }
  
  return(df)
}

# Main loop over subject directories
subject_dirs <- list.dirs(base_dir, recursive = FALSE, full.names = TRUE)

for (subject_dir in subject_dirs) {
  subject_folder <- basename(subject_dir)
  # Extract subject ID and build new folder name
  subject_id <- str_remove(subject_folder, "^output_")
  subject_label <- paste0("sub-", subject_id)
  
  # Set up the corresponding output directory (sub-<ID>/actigraphy)
  output_results_dir <- file.path(output_dir, subject_label, "actigraphy")
  dir.create(output_results_dir, recursive = TRUE, showWarnings = FALSE)
  
  results_dir <- file.path(subject_dir, "results")
  
  for (file_name in file_names) {
    file_path <- file.path(results_dir, file_name)
    processed_df <- process_file(file_path, file_name)
    if (!is.null(processed_df)) {
      # Determine level
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
      write_tsv(processed_df, out_path, na = "n/a")
    }
  }
}

# Copy and convert config.csv to config.tsv for each subject
for (subject_dir in subject_dirs) {
  subject_folder <- basename(subject_dir)
  subject_id <- str_remove(subject_folder, "^output_")
  subject_label <- paste0("sub-", subject_id)
  config_csv <- file.path(subject_dir, "config.csv")
  # Place config.tsv in sub-<ID>/actigraphy/
  config_tsv_out <- file.path(output_dir, subject_label, "actigraphy", paste0(subject_label, "_config.tsv"))
  if (file.exists(config_csv)) {
    config_df <- read_csv(config_csv, show_col_types = FALSE)
    write_tsv(config_df, config_tsv_out, na = "n/a")
  }
}
