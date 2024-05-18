library(gtsummary)
library(dplyr)

# 데이터 불러오기
data <- read.csv("cohort_final2.csv")

# 'tof_group' 레이블 정의
data$tof_group <- factor(data$tof_group,
                         levels = c(1, 2, 3),
                         labels = c("Patients diagnosed with TOF",
                                    "Patients diagnosed with TOF with pulmonary atresia",
                                    "Patients diagnosed with both TOF and TOF with pulmonary atresia"))

# 전체 그룹 "TOF Total" 추가
data_total <- data %>%
  mutate(group_analysis = "TOF Total")

# 개별 그룹 레이블 추가
data$group_analysis <- as.character(data$tof_group)

# 데이터 결합: 원본 그룹과 "TOF Total" 그룹 데이터
data_long <- bind_rows(data_total, data)

# 'group_analysis' 팩터 레벨 조정
data_long$group_analysis <- factor(data_long$group_analysis,
                                   levels = c("TOF Total", "Patients diagnosed with TOF",
                                              "Patients diagnosed with TOF with pulmonary atresia",
                                              "Patients diagnosed with both TOF and TOF with pulmonary atresia"))

# 'is_procedure'를 팩터로 변환하고 레이블 추가
data_long$is_procedure <- factor(data_long$is_procedure,
                                 levels = c(0, 1),
                                 labels = c("No Surgery", "Surgery"))

# 연령 변수 생성 및 범주화
data_long <- data_long %>%
  mutate(Age = baseline_age,
         Age_Category = ifelse(Age < 18, "Under 18", "18 and above")) %>%
  select(-baseline_age)

# 'Age_Category'를 팩터로 변환하고 레벨 지정
data_long$Age_Category <- factor(data_long$Age_Category,
                                 levels = c("Under 18", "18 and above"))

# 'gender'를 팩터로 변환하고 레벨 지정
data_long$gender <- factor(data_long$gender,
                           levels = c("F", "M"))

# 기본 특성 테이블 생성 및 p-값 추가
table <- tbl_summary(
  data_long,
  by = "group_analysis",
  include = c("Age", "Age_Category", "height", "weight", "bmi", "gender", "is_procedure"),
  statistic = list(
    all_continuous() ~ "{mean} ({sd})",
    all_categorical() ~ "{N} ({p}%)"
  ),
  type = list(
    is_procedure ~ "categorical"
  )
) %>%
  add_p()

# 결과 출력
print(table)