library(gtsummary)
library(dplyr)

# Load the data
data <- read.csv("cohort_final.csv")

# Define labels for 'tof_group'
data$tof_group <- factor(data$tof_group,
                         levels = c(1, 2, 3),
                         labels = c("Patients diagnosed with TOF",
                                    "Patients diagnosed with TOF with pulmonary atresia",
                                    "Patients diagnosed with both TOF and TOF with pulmonary atresia"))

# Add a new column 'group_analysis' including TOF Total group
data$group_analysis <- factor(
  rep("TOF Total", nrow(data)),
  levels = c("TOF Total", "Patients diagnosed with TOF",
             "Patients diagnosed with TOF with pulmonary atresia",
             "Patients diagnosed with both TOF and TOF with pulmonary atresia")
)

# Combine the existing groups with TOF Total and adjust the data
data_long <- bind_rows(
  data %>% mutate(group_analysis = "TOF Total"),
  data %>% mutate(group_analysis = as.character(tof_group))
)

# Adjust the order of factor levels in 'group_analysis'
data_long$group_analysis <- factor(data_long$group_analysis,
                                   levels = c("TOF Total", "Patients diagnosed with TOF",
                                              "Patients diagnosed with TOF with pulmonary atresia",
                                              "Patients diagnosed with both TOF and TOF with pulmonary atresia"))

# Create 'Age' and divide it into 'Age_Category'
data_long <- data_long %>%
  mutate(Age = baseline_age,
         Age_Category = ifelse(baseline_age < 18, "Under 18", "18 and above")) %>%
  select(-baseline_age)

# Create baseline characteristic table
table <- tbl_summary(
  data_long,
  by = "group_analysis", # Grouping by 'group_analysis'
  include = c("Age", "Age_Category", "height", "weight", "bmi", "gender"), # Selecting variables to include
  statistic = list(all_continuous() ~ "{mean} ({sd})") # Statistics for continuous variables
)

# Display the results
table
