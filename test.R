# 필요한 라이브러리 로드
library(gtsummary)
library(dplyr)
library(purrr)

# 데이터 로드
data <- read.csv("cohort_final2.csv")

# 성별을 범주형 변수로 변환
df$gender <- as.factor(df$gender)

# Age를 Age_Category로 변환
df <- df %>%
  mutate(Age_Category = ifelse(age < 18, 'Under 18', '18 and above'))

# 테이블 생성 함수 정의
create_summary_table <- function(data, by_var = NULL) {
  summary <- data %>%
    select(gender, baseline_age, Age_Category, age, height, weight, bmi, is_procedure, all_of(by_var)) %>%
    tbl_summary(
      by = if (!is.null(by_var)) all_of(by_var) else NULL,
      statistic = list(
        all_continuous() ~ "{mean} ({sd})",
        all_categorical() ~ "{n} / {N} ({p}%)"
      ),
      missing = "no"
    )
  
  if (!is.null(by_var)) {
    summary <- summary %>%
      add_p() %>%
      modify_header(label ~ "**Variable**") %>%
      modify_spanning_header(list(everything() ~ by_var))
  }
  
  summary <- summary %>%
    bold_labels()
  
  return(summary)
}

# 전체 요약 테이블 생성
summary_table_total <- create_summary_table(df)

# 심방빈맥에 따른 요약 테이블 생성
summary_table_AF <- create_summary_table(df, "AF")

# 심실빈맥에 따른 요약 테이블 생성
summary_table_VT <- create_summary_table(df, "VT")

# 테이블 합치기
combined_table <- tbl_merge(
  tbls = list(summary_table_total, summary_table_AF, summary_table_VT),
  tab_spanner = c("**Overall**", "**Atrial Flutter/Fibrillation (AF)**", "**Ventricular Tachycardia (VT)**")
)

# 결과 출력
combined_table
