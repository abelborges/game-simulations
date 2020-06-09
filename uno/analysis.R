library(dplyr)
library(tidyr)
library(readr)
library(stringr)
library(ggplot2)
options(readr.num_columns = 0)

# files = paste0("data/game_", 1:20000, ".csv")
# ds = vector("list", length(files))
# for(i in seq_along(ds)) {
#   if(i %% 1000 == 0) print(i/length(ds))
#   ds[[i]] = read_csv(files[i])
# }
# d = do.call(bind_rows, ds)
# write_csv(d, "data/first_20k.csv")

d = read_csv("data/first_20k.csv")

# s = d %>%
#   group_by(game_id) %>%
#   summarise(n = n_distinct(round_id)) %>%
#   select(n)
# 
# write_csv(s, "data/stats/round_counts.csv")

s = read_csv("data/stats/round_counts.csv")

s %>%
  count(n) %>%
  arrange(n) %>%
  transmute(
    N = n,
    p = nn/sum(nn),
    cum_p = cumsum(p)
  ) %>%
  filter(cum_p < 1) %>%
  ggplot(aes(N, p)) +
  geom_line(lwd = 1) +
  scale_y_continuous(name = "% of games ending after N plays",
                     breaks = seq(0, 1, by = .01),
                     labels = scales::percent) +
  scale_x_continuous(breaks = seq(0, 500, by = 20)) +
  theme_light(base_size = 15)
