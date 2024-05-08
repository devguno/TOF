library(gtsummary)
library(dplyr)
library(forcats)

# 데이터 불러오기
data <- read.csv("tof_final_cohort_drug_with_group.csv")

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

# 약제 처방 빈도 테이블 생성
drug_table <- tbl_summary(
  data_long,
  by = "group_analysis", # 'group_analysis'로 그룹화
  include = "drug_category", # drug_category 변수 포함
  statistic = all_categorical() ~ "{n} ({p}%)" # 범주형 변수에 대한 통계
) 

# 결과 보기
print(drug_table)