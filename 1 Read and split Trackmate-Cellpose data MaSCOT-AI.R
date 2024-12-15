library(dplyr)
library(readr)
library(writexl)
library(tibble)

# Enter the filepath for the folder containing trackmate-Cellpose stats files as csv
file_list <- list.files(path = "/spotStats", pattern = "*.csv", full.names = TRUE)

# Initialize lists to store data for each measurement
ellipse_aspectratio_list <- list()
area_list <- list()
perimeter_list <- list()
circularity_list <- list()
solidity_list <- list()
shape_index_list <- list()

# Loop over each file
for (file in file_list) {
  # Read the CSV file
  data <- read_csv(file)
  
  # Extract the necessary columns and arrange by FRAME
  data <- data %>%
    dplyr::select(TRACK_ID, FRAME, ELLIPSE_ASPECTRATIO, AREA, PERIMETER, CIRCULARITY, SOLIDITY, SHAPE_INDEX) %>%
    dplyr::arrange(FRAME)
  
  # Split the data by TRACK_ID and store in the lists
  ellipse_aspectratio_list[[file]] <- data %>%
    dplyr::select(TRACK_ID, FRAME, ELLIPSE_ASPECTRATIO) %>%
    split(.$TRACK_ID)
  area_list[[file]] <- data %>%
    dplyr::select(TRACK_ID, FRAME, AREA) %>%
    split(.$TRACK_ID)
  perimeter_list[[file]] <- data %>%
    dplyr::select(TRACK_ID, FRAME, PERIMETER) %>%
    split(.$TRACK_ID)
  circularity_list[[file]] <- data %>%
    dplyr::select(TRACK_ID, FRAME, CIRCULARITY) %>%
    split(.$TRACK_ID)
  solidity_list[[file]] <- data %>%
    dplyr::select(TRACK_ID, FRAME, SOLIDITY) %>%
    split(.$TRACK_ID)
  shape_index_list[[file]] <- data %>%
    dplyr::select(TRACK_ID, FRAME, SHAPE_INDEX) %>%
    split(.$TRACK_ID)
}

# Write the lists to new Excel files - optional and doesn't work yet
# write_xlsx(ellipse_aspectratio_list, "ellipse_aspectratio.xlsx")
# write_xlsx(area_list, "area.xlsx")
# write_xlsx(perimeter_list, "perimeter.xlsx")
# write_xlsx(circularity_list, "circularity.xlsx")
# write_xlsx(solidity_list, "solidity.xlsx")
# write_xlsx(shape_index_list, "shape_index.xlsx")

#filter out track ID with value 'TRACK_ID' - also doesn't work, we do this later
ellipse_aspectratio_list_filt <- ellipse_aspectratio_list %>% filter(TRACK_ID != "Track ID")
area_list_filt <- area_list %>% filter(TRACK_ID != "Track ID")
perimeter_list_filt <- perimeter_list %>% filter(TRACK_ID != "Track ID")
circularity_list_filt <- circularity_list %>% filter(TRACK_ID != "Track ID")
solidity_list_filt <- solidity_list %>% filter(TRACK_ID != "Track ID")
shape_index_list_filt <- shape_index_list %>% filter(TRACK_ID != "Track ID")


# Create new filtered lists to save processed data
ellipse_aspectratio_list_filt <- ellipse_aspectratio_list
area_list_filt <- area_list
perimeter_list_filt <- perimeter_list
circularity_list_filt <- circularity_list
solidity_list_filt <- solidity_list
shape_index_list_filt <- shape_index_list

# List of all your lists for looping
all_lists <- list(ellipse_aspectratio_list, area_list, perimeter_list, circularity_list, solidity_list, shape_index_list)

# List of all your list names for looping
all_list_names <- c("ellipse_aspectratio_list", "area_list", "perimeter_list", "circularity_list", "solidity_list", "shape_index_list")

# Function to process each list
process_list <- function(list, list_name) {
  # Create a tibble
  data <- tibble(TRACK_ID = list$TRACK_ID, FRAME = list$FRAME, MEASUREMENT = list$MEASUREMENT)
  
  # Filter out rows with "Track ID" in the Track ID column
  data <- data %>% filter(TRACK_ID != "Track ID")
  
  # Add the list name as the first row
  data <- add_row(data, TRACK_ID = list_name, FRAME = NA, MEASUREMENT = NA, .before = 1)
  
  # Return the processed data
  return(data)
}

# Process each list and save the result as an XLSX file
for (i in seq_along(all_lists)) {
  # Process the list
  data <- process_list(all_lists[[i]], all_list_names[i])
  
  # Save the result as an XLSX file
  write_xlsx(data, paste0(all_list_names[i], ".xlsx"))
}

# Assuming 'list_name' is one of your lists
# And 'measurement_name' is the corresponding measurement name

list_names <- list(ellipse_aspectratio_list, area_list, perimeter_list, circularity_list, solidity_list, shape_index_list)
measurement_names <- c("ELLIPSE_ASPECTRATIO", "AREA", "PERIMETER", "CIRCULARITY", "SOLIDITY", "SHAPE_INDEX")

for (j in 1:length(list_names)) {
  list_name <- list_names[[j]]
  measurement_name <- measurement_names[j]
  
  for (i in 1:length(list_name)) {
    # Exclude data where the second element is "Track ID"
    if (list_name[[i]][2] != "Track ID") {
      data <- list_name[[i]]
      
      # Create a tibble
      df <- tibble(
        FileName = gsub(".csv", "", basename(data$FilePath)),
        TrackID = data$TRACK_ID,
        Frame = data$FRAME,
        Measurement = data[[measurement_name]]
      )
      
      # Write the tibble to an xlsx file
      write_xlsx(df, path = paste0(getwd(), "/FileName_", i, "2_", measurement_name, ".xlsx"))
    }
  }
}