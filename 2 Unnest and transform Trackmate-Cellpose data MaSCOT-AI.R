library(dplyr)
library(readr)
library(writexl)
library(purrr)
library(ggplot2)
library(tools)
library(nplyr)
library(magrittr)
library(stringr)

  # Replace MEASUREMENT with the measurement_list (eg. solidity_list) here and also on lines 35 and 78
  # Assuming 'nested_list' is your nested list
  unnested_list <- MEASUREMENT_list %>%
    purrr::map_df(~ .x %>%
                    dplyr::bind_rows(), .id = "id")
  
  # Trim the first column to just the file name
  unnested_list$id <- basename(unnested_list$id)
  
  #combine the file name and track id so that spreading of frames works later
  unnested_list_combID <- unnested_list %>%
    unite(file_track_id, id, TRACK_ID, sep = "_", remove = TRUE) %>%
    select(file_track_id, everything())
  
  # Name the df to make wide (transpose FRAME and put value within that)
  unnested_list_filt <- unnested_list_combID
  
  # Filter out rows with "Track ID" in file_track_id - these created duplicates that messed with transposition
  unnested_list_filt <- unnested_list_combID %>%
    filter(!str_detect(file_track_id, "Track ID$"))
  
  # change "MEASUREMENT" value to measurement column title (ELLIPSE_ASPECTRATIO, AREA, PERIMETER, CIRCULARITY, SOLIDITY, or SHAPE_INDEX)
  # Convert the data to wide format
  unnested_list_wide <- unnested_list_filt %>%
    pivot_wider(names_from = FRAME, values_from = MEASUREMENT)
  
  # Extract the numeric part of the column names
  num <- as.numeric(gsub("FRAME", "", colnames(unnested_list_wide)))
  
  # Create a named vector for reordering the columns
  cols_order <- setNames(colnames(unnested_list_wide), num)
  
  # Exclude the 'file_track_id' column
  cols_order <- cols_order[cols_order != 'file_track_id']
  
  # Sort the named vector
  cols_order <- cols_order[order(as.numeric(names(cols_order)))]
  
  # Add 'file_track_id' at the beginning
  cols_order <- c('file_track_id', cols_order)
  
  # Reorder the columns of the data frame
  unnested_list_ordered <- unnested_list_wide[, cols_order]
  
  # Remove unwanted timepoints (here columns 31 to 37, after 5 hours of imaging when cell death increased) - hash out if not needed
  #unnested_list_ordered <- select(unnested_list_ordered, c(`31`, `32`, `33`, `34`, `35`, `36`, `37`))
  
  # Add a second column based on strings detected in the first column
  # This is to create sample labels for sorting later. Edit logic accordingly based on your file names.
  unnested_list_ordered_label <- unnested_list_ordered %>%
    mutate(label = case_when(
      grepl("K5", file_track_id, ignore.case = TRUE) ~ "K5 TEB",
      grepl("PR", file_track_id, ignore.case = TRUE) & !grepl("duct|plug|MPA|notpreg|preg", file_track_id, ignore.case = TRUE) ~ "PR TEB",
      grepl("PR", file_track_id, ignore.case = TRUE) & grepl("preg|plug", file_track_id, ignore.case = TRUE) & !grepl("notpreg", file_track_id, ignore.case = TRUE) ~ "PR duct preg",
      grepl("PR", file_track_id, ignore.case = TRUE) & grepl("MPA", file_track_id, ignore.case = TRUE) & !grepl("veh", file_track_id, ignore.case = TRUE) ~ "PR duct MPA",
      grepl("PR", file_track_id, ignore.case = TRUE) & grepl("veh", file_track_id, ignore.case = TRUE) ~ "PR duct VEH",
      grepl("PR", file_track_id, ignore.case = TRUE) & grepl("duct|notpreg", file_track_id, ignore.case = TRUE) ~ "PR duct",
      grepl("Elf5", file_track_id, ignore.case = TRUE) & !grepl("duct", file_track_id, ignore.case = TRUE) ~ "Elf5 TEB",
      grepl("Elf5", file_track_id, ignore.case = TRUE) & grepl("duct", file_track_id, ignore.case = TRUE) ~ "Elf5 duct",
      TRUE ~ as.character(file_track_id)
    ))
  
  # Move the label column to the second position
  unnested_list_ordered_label <- unnested_list_ordered_label[, c(1, which(colnames(unnested_list_ordered_label)=="label"), 2:(ncol(unnested_list_ordered_label)-1))]
  
  # Save the data frame as a .csv file
  # specify your expoert directory and replace MEASUREMENT with the measurement_list used
  write.csv(unnested_list_ordered_label, file = "/.../trackmate_cellpose_MEASUREMENT.csv")
  
  
  