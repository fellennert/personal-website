#!/usr/bin/env Rscript
# Run all classifiers on IMDb reviews: 500 train, same test set.
# Writes results to classifier_results.csv and optionally runs BERT via reticulate (bert-env).

BASE <- file.path(getwd(), "files_for_project_backlog", "ml_classifiers")
if (!dir.exists(BASE)) BASE <- dirname(sys.frame(1)$ofile)
setwd(BASE)

needs(tidyverse, tidytext, textrecipes, tidymodels, workflows, yardstick, discrim,
      naivebayes, SnowballC, stopwords, textdata, tictoc, jsonlite,
      glmnet, LiblineaR, ranger, xgboost)

# Data: use local CSV (review -> text)
imdb_raw <- read_csv("imdb-reviews.csv", show_col_types = FALSE) |>
  rename(text = review)

# Stratified split: 500 train, rest test
set.seed(123)
split <- initial_split(imdb_raw, prop = 500 / nrow(imdb_raw), strata = sentiment)
imdb_train <- training(split)
imdb_test <- testing(split)

# Write splits for Python BERT
imdb_train |> write_csv("train_split.csv")
imdb_test |> write_csv("test_split.csv")

# Shared recipes: same preprocessing for all BoW models; SVM needs normalize as last step
recipe_bow <- recipe(sentiment ~ text, data = imdb_train) |>
  step_tokenize(text) |>
  step_tokenfilter(text, max_tokens = 1000) |>
  step_tfidf(text)

recipe_svm <- recipe(sentiment ~ text, data = imdb_train) |>
  step_tokenize(text) |>
  step_tokenfilter(text, max_tokens = 1000) |>
  step_tfidf(text) |>
  step_normalize(all_predictors())

# Helper: fit workflow, augment on test, compute metrics with tictoc
run_bow <- function(name, wf, label_tic = name) {
  tic(label_tic)
  fit_wf <- fit(wf, data = imdb_train)
  pred <- augment(fit_wf, imdb_test)
  elapsed <- toc(quiet = TRUE)
  pred |>
    metric_set(accuracy, precision, recall, f_meas)(
      truth = sentiment,
      estimate = .pred_class,
      event_level = "second"
    ) |>
    pivot_wider(names_from = .metric, values_from = .estimate) |>
    mutate(
      classifier = name,
      runtime_seconds = round(elapsed, 2),
      .before = 1
    ) |>
    rename(f1 = f_meas) |>
    select(classifier, accuracy, precision, recall, f1, runtime_seconds)
}

# ---- 1. Dictionary-based (AFINN) ----
tic("Dictionary (AFINN)")
afinn_stemmed <- get_sentiments("afinn") |>
  mutate(stemmed = wordStem(word, language = "en"))
scored <- imdb_test |>
  rowid_to_column("doc") |>
  unnest_tokens(token, text) |>
  anti_join(get_stopwords(), by = c("token" = "word")) |>
  mutate(stemmed = wordStem(token, language = "en")) |>
  inner_join(afinn_stemmed, by = "stemmed", relationship = "many-to-many") |>
  group_by(doc) |>
  summarise(sentiment_score = mean(value), .groups = "drop") |>
  mutate(
    .pred_class = if_else(sentiment_score > 0, "positive", "negative"),
    .pred_class = factor(.pred_class, levels = c("positive", "negative"))
  )
imdb_afinn <- imdb_test |>
  rowid_to_column("doc") |>
  select(doc, sentiment) |>
  mutate(sentiment = factor(sentiment, levels = c("positive", "negative"))) |>
  left_join(select(scored, doc, .pred_class), by = "doc") |>
  mutate(
    .pred_class = replace_na(as.character(.pred_class), "positive"),
    .pred_class = factor(.pred_class, levels = c("positive", "negative"))
  )
dict_time <- toc(quiet = TRUE)
dict_metrics <- imdb_afinn |>
  metric_set(accuracy, precision, recall, f_meas)(
    truth = sentiment,
    estimate = .pred_class,
    event_level = "second"
  ) |>
  pivot_wider(names_from = .metric, values_from = .estimate) |>
  mutate(
    classifier = "Dictionary (AFINN)",
    runtime_seconds = round(dict_time, 2),
    .before = 1
  ) |>
  rename(f1 = f_meas) |>
  select(classifier, accuracy, precision, recall, f1, runtime_seconds)

# ---- 2. Bag-of-words classifiers (same preprocessing) ----
wf_nb <- workflow() |> add_recipe(recipe_bow) |> add_model(
  naive_Bayes() |> set_engine("naivebayes") |> set_mode("classification")
)
wf_glm <- workflow() |> add_recipe(recipe_bow) |> add_model(
  logistic_reg() |> set_engine("glm") |> set_mode("classification")
)
wf_lasso <- workflow() |> add_recipe(recipe_bow) |> add_model(
  logistic_reg(penalty = 0.01, mixture = 1) |> set_engine("glmnet") |> set_mode("classification")
)
wf_ridge <- workflow() |> add_recipe(recipe_bow) |> add_model(
  logistic_reg(penalty = 0.01, mixture = 0) |> set_engine("glmnet") |> set_mode("classification")
)
wf_svm <- workflow() |> add_recipe(recipe_svm) |> add_model(
  svm_linear() |> set_engine("LiblineaR") |> set_mode("classification")
)
wf_rf <- workflow() |> add_recipe(recipe_bow) |> add_model(
  rand_forest(trees = 100) |> set_engine("ranger") |> set_mode("classification")
)
wf_xgb <- workflow() |> add_recipe(recipe_bow) |> add_model(
  boost_tree(trees = 50) |> set_engine("xgboost") |> set_mode("classification")
)

bow_metrics <- bind_rows(
  run_bow("Naive Bayes (TF-IDF)", wf_nb, "Naive Bayes (TF-IDF)"),
  run_bow("Logistic regression (glm)", wf_glm, "Logistic regression (glm)"),
  run_bow("Lasso (glmnet)", wf_lasso, "Lasso (glmnet)"),
  run_bow("Ridge (glmnet)", wf_ridge, "Ridge (glmnet)"),
  run_bow("SVM linear (LiblineaR)", wf_svm, "SVM linear (LiblineaR)"),
  run_bow("Random forest (ranger)", wf_rf, "Random forest (ranger)"),
  run_bow("XGBoost", wf_xgb, "XGBoost")
)

# ---- 3. BERT (Python, bert-env) ----
bert_metrics <- tryCatch({
  reticulate::use_condaenv("bert-env", required = TRUE)
  python_exe <- reticulate::conda_python("bert-env")
  system2(python_exe, file.path(BASE, "run_bert.py"))
  bert_res <- jsonlite::read_json("bert_results.json")
  tibble(
    classifier = "BERT (fine-tuned)",
    accuracy = bert_res$accuracy,
    precision = bert_res$precision,
    recall = bert_res$recall,
    f1 = bert_res$f1,
    runtime_seconds = bert_res$runtime_seconds
  )
}, error = function(e) {
  message("BERT skipped: ", conditionMessage(e))
  tibble(classifier = "BERT (fine-tuned)", accuracy = NA_real_, precision = NA_real_,
         recall = NA_real_, f1 = NA_real_, runtime_seconds = NA_real_)
})

# ---- 4. LLM (zero-shot, ellmer/Ollama) ----
gpt_metrics <- tryCatch({
  needs(ellmer, ollamar)
  n_gpt <- 100
  imdb_test_gpt <- imdb_test |> slice_head(n = n_gpt)
  sentiment_type <- ellmer::type_object(
    sentiment = ellmer::type_enum("Sentiment of the review", values = c("positive", "negative"))
  )
  ref_prompt_sentiment <- "
You are a movie expert. Classify the sentiment of the review as positive or negative.
Code as 'positive' if the review expresses enjoyment, praise, or recommendation.
Code as 'negative' if it expresses dislike, criticism, or recommends against watching.
If mixed, code by overall tone. Reply with the single word: positive or negative.
"
  tic("LLM zero-shot")
  gpt_preds <- map(imdb_test_gpt$text, function(txt) {
    ch <- ellmer::chat_ollama(
      model = "qwen2.5:3b",
      system_prompt = ref_prompt_sentiment,
      params = ellmer::params(temperature = 0.1, seed = 42)
    )
    out <- ch$chat_structured(txt, type = sentiment_type)
    as.character(out$sentiment)
  }, .progress = TRUE)
  gpt_time <- toc(quiet = TRUE)
  gpt_df <- imdb_test_gpt |>
    select(sentiment) |>
    mutate(
      .pred_class = factor(unlist(gpt_preds), levels = c("positive", "negative")),
      sentiment = factor(sentiment, levels = c("positive", "negative"))
    )
  gpt_df |>
    metric_set(accuracy, precision, recall, f_meas)(
      truth = sentiment,
      estimate = .pred_class,
      event_level = "second"
    ) |>
    pivot_wider(names_from = .metric, values_from = .estimate) |>
    mutate(
      classifier = paste0("LLM zero-shot (n=", n_gpt, ")"),
      runtime_seconds = round(gpt_time, 2),
      .before = 1
    ) |>
    rename(f1 = f_meas) |>
    select(classifier, accuracy, precision, recall, f1, runtime_seconds)
}, error = function(e) {
  message("LLM skipped: ", conditionMessage(e))
  tibble(classifier = "LLM zero-shot (n=100)", accuracy = NA_real_, precision = NA_real_,
         recall = NA_real_, f1 = NA_real_, runtime_seconds = NA_real_)
})

# ---- Bind and save ----
results <- bind_rows(dict_metrics, bow_metrics, bert_metrics, gpt_metrics)
write_csv(results, "classifier_results.csv")
print(results)
