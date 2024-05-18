library(gtsummary)
library(dplyr)
library(forcats)
library(flextable)

# 데이터 불러오기
data <- read.csv("cohort_final_ecg2.csv")

# 'tof_group' 레이블 정의
data$tof_group <- factor(data$tof_group,
                         levels = c(1, 2, 3),
                         labels = c("Patients diagnosed with TOF",
                                    "Patients diagnosed with TOF with pulmonary atresia",
                                    "Patients diagnosed with both TOF and TOF with pulmonary atresia"))

# 'group_analysis' 컬럼 추가, "TOF Total" 그룹 포함
data$group_analysis <- factor(
  rep("TOF Total", nrow(data)),
  levels = c("TOF Total", "Patients diagnosed with TOF",
             "Patients diagnosed with TOF with pulmonary atresia",
             "Patients diagnosed with both TOF and TOF with pulmonary atresia")
)

# 기존 그룹과 "TOF Total" 그룹을 결합하고 데이터 조정
data_long <- bind_rows(
  data %>% mutate(group_analysis = "TOF Total"),
  data %>% mutate(group_analysis = as.character(tof_group))
)

# 'group_analysis' 팩터 레벨 순서 조정
data_long$group_analysis <- factor(data_long$group_analysis,
                                   levels = c("TOF Total", "Patients diagnosed with TOF",
                                              "Patients diagnosed with TOF with pulmonary atresia",
                                              "Patients diagnosed with both TOF and TOF with pulmonary atresia"))

# ECG 결과의 기본 특성 테이블 생성
table <- tbl_summary(
  data_long,
  by = "group_analysis", # 'group_analysis'로 그룹화
  include = c("VentricularRate", "PRInterval", "QRSDuration", "QTInterval", "QTCorrected",
              "Paxis", "Raxis", "Taxis", "Qonset", "Qoffset", "Ponset", "Poffset", "QTcFrederica"), # ECG 변수 포함
  statistic = all_continuous() ~ "{mean} ± {sd} ({min}, {max})", # 연속 변수에 대한 통계
  missing = "no" # 결측치 표시하지 않음
) %>%
  add_p() # p-값 추가

# 결과 출력
print(table)