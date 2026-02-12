needs(tidyverse, hms, plotly)

read_csv("projects/boston_marathon_data/strava_results_4.csv") |> write_csv("projects/boston_marathon_data/strava_results.csv")

boston_data <- read_csv("projects/boston_marathon_data/strava_results.csv") |>
  select(-1) |>
  distinct(date, run_data, gear, .keep_all = TRUE) |>
  rowid_to_column("rank") |>
  separate(
    run_data,
    into = c(
      "distance",
      "scrap_1",
      "elapsed_time",
      "scrap_2",
      "pace",
      "scrap_3",
      "relative_effort",
      "scrap_4"
    ),
    sep = "\\n"
  ) |>
  separate(gear, into = c("device", "shoes"), sep = "\\n") |>
  mutate(
    pace = pace |>
      str_extract("[0-9]:[0-9]{2}") |>
      str_c("00:", x = _) |>
      parse_hms(),
    distance = distance |> str_remove(" km$") |> parse_double(),
    relative_effort = parse_double(relative_effort),
    elapsed_time = parse_hms(elapsed_time),
    date = str_remove(date, "^[A-Za-z]*, ") |> parse_date(format = "%B %d, %Y")
  ) |>
  select(rank:distance, pace, elapsed_time, relative_effort, device, shoes) |>
  filter(date == ymd("2025-04-21") & distance > 42)

watches <- boston_data |>
  select(rank, device) |>
  filter(!str_detect(device, "Shoe")) |>
  mutate(
    watch_brand = device |> str_to_lower() |> str_extract("^[a-z]*"),
    watch_model = device |>
      str_to_lower() |>
      str_remove("^[a-z]*") |>
      str_squish()
  ) |>
  group_by(watch_brand) |>
  filter(n() > 5) |>
  mutate(
    watch_model_cat = case_when(
      watch_brand == "garmin" ~ str_extract(watch_model, "^[\\w]*"),
      watch_brand == "coros" ~ str_extract(watch_model, "^[a-z]*"),
      watch_brand == "apple" & str_detect(watch_model, "ultra") ~ "watch ultra",
      watch_brand == "apple" & str_detect(watch_model, "se\\b") ~ "watch se",
      watch_brand == "apple" & str_detect(watch_model, "watch") ~ "watch",
      watch_brand == "suunto" ~ str_extract(watch_model, "^[1-9a-z]*"),
      watch_brand == "polar" ~ str_extract(watch_model, "^[1-9a-z]*"),
      TRUE ~ NA_character_
    )
  )

shoes <- boston_data |>
  select(rank, shoes) |>
  mutate(
    shoe_km = shoes |>
      str_extract("\\([0-9,\\.]* km\\)") |>
      str_remove_all("[(),km]") |>
      parse_double(),
    shoe_brand = shoes |>
      str_remove(r"(Shoes: )") |>
      str_remove(" \\([0-9].*$") |>
      str_to_lower() |>
      str_replace_all("new balance", "nb") |>
      str_extract("^[a-z]*"),
    shoe_model = shoes |>
      str_remove(r"(Shoes: )") |>
      str_remove(" \\([0-9].*$") |>
      str_to_lower() |>
      str_replace_all("new balance", "nb") |>
      str_remove("^[a-z]*") |>
      str_squish()
  ) |>
  filter(!str_length(shoe_brand) == 0) |>
  filter(shoe_km < 1000) |>
  group_by(shoe_brand) |>
  filter(n() > 5) |>
  ungroup()

needs(ollamar, ellmer)
ollamar::pull("qwen2.5:7b")
shoe_model <- type_object(
  model = type_string("extracted model")
)

ref_prompt_structured <- "
You are a running shoe expert trying to categorize running shoes. 

INSTRUCTIONS: extract the running shoe model from the running shoe entry. 
  Try to keep it broad, but with enough detail.

  Examples: 
    - 'ASICS Metaspeed Sky 4' should become 'Metaspeed Sky 4'
    - 'Adidas Adizero Adios Pro Evo 1' should become 'Adizero Adios Pro Evo 1'
    - 'Nike Vaporfly Next% 3 - 2' should become 'Nike Vaporfly Next% 3'
"

shoe_classifier <- chat_ollama(
  model = "qwen2.5:7b",
  system_prompt = ref_prompt_structured,
  params = params(
    temperature = 0.2, # low for consistency
    seed = 42 # Reproducible results
  )
)

model_classification <- boston_data |>
  select(rank, shoes) |>
  mutate(
    shoe_km = shoes |>
      str_extract("\\([0-9,\\.]* km\\)") |>
      str_remove_all("[(),km]") |>
      parse_double(),
    shoe_brand = shoes |>
      str_remove(r"(Shoes: )") |>
      str_remove(" \\([0-9].*$") |>
      str_to_lower() |>
      str_replace_all("new balance", "nb") |>
      str_extract("^[a-z]*"),
    shoe_model = shoes |>
      str_remove(r"(Shoes: )") |>
      str_remove(" \\([0-9].*$") |>
      str_to_lower() |>
      str_replace_all("new balance", "nb") |>
      str_remove("^[a-z]*") |>
      str_squish()
  ) |>
  filter(!str_length(shoe_brand) == 0) |>
  filter(shoe_km < 1000) |>
  dplyr::pull(shoe_model) |>
  enframe(name = NULL, value = "x") |>
  rowid_to_column("id") |>
  pmap(
    \(x, id) {
      if ((id - 1) %% 20 == 0) {
        classifier <<- chat_ollama(
          model = "qwen2.5:7b",
          system_prompt = ref_prompt_structured,
          params = params(
            temperature = 0.2,
            seed = 42
          )
        )
      }
      classifier$chat_structured(x, type = shoe_model)
    },
    .progress = TRUE
  )

models <- model_classification |>
  bind_rows() |>
  mutate(
    model = str_to_lower(model) |>
      str_remove_all("[0-9]|next%|adizero|zoomx|air zoom") |>
      str_squish() |>
      str_replace_all(
        c(
          "alpha fly" = "alphafly",
          "fast.?r.*" = "fast-r",
          "alphafly.*" = "alphafly",
          "a fly" = "alphafly",
          "^alpha$" = "alphafly",
          "meta.?speed.*" = "metaspeed",
          "^af.*$" = "alphafly",
          "alphaphly" = "alphafly",
          "cloud.?boom .*" = "cloudboom",
          "^pro$" = "adios pro",
          "adios pro evo" = "adios pro",
          "vaporfly.*" = "vaporfly",
          "hype elite" = "hyperion elite",
          "cielo x.*" = "cielo",
          "rocket x.*" = "rocket",
          "sc" = "supercomp",
          "sc" = "supercomp",
          "fuelcell supercomp" = "supercomp",
          "feulcell supercomp" = "supercomp",
          "fuelcell rc" = "supercomp",
          "nike " = "",
          "vapor$" = "vaporfly",
          "vf.*" = "vaporfly",
          "deviate.*" = "deviate",
          "endorphin.*" = "endorphin",
          "^alpha s$" = "alphafly",
          " v$" = ""
        )
      ),
    model = str_replace(model, "supercomp elite", "fuelcell supercomp elite")
  )

t <- boston_data |>
  select(rank, shoes) |>
  mutate(
    shoe_km = shoes |>
      str_extract("\\([0-9,\\.]* km\\)") |>
      str_remove_all("[(),km]") |>
      parse_double(),
    shoe_brand = shoes |>
      str_remove(r"(Shoes: )") |>
      str_remove(" \\([0-9].*$") |>
      str_to_lower() |>
      str_replace_all("new balance", "nb") |>
      str_extract("^[a-z]*"),
    shoe_model = shoes |>
      str_remove(r"(Shoes: )") |>
      str_remove(" \\([0-9].*$") |>
      str_to_lower() |>
      str_replace_all("new balance", "nb") |>
      str_remove("^[a-z]*") |>
      str_squish()
  ) |>
  filter(!str_length(shoe_brand) == 0) |>
  filter(shoe_km < 1000) |>
  bind_cols(models) |>
  write_csv("projects/boston_marathon_data/boston_shoe_models.csv")
