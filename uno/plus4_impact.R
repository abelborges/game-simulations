library(dplyr)
library(tidyr)
library(readr)
library(stringr)
library(ggplot2)

#setwd("~/repos/game-simulations/uno/")
d = read_csv("plus4_impact.csv") %>%
  gather("player", "plus4s", -winner, -replicate_id) %>%
  mutate(player = substr(player, 8, 8)) %>%
  mutate(winner = player == as.character(winner)) %>%
  select(replicate_id, player, winner, plus4s) %>%
  arrange(replicate_id, player)

# distribution os plus4s per game
d %>%
  group_by(replicate_id) %>%
  summarise(plus4s = sum(plus4s)) %>%
  count(plus4s) %>%
  mutate(p = n / sum(n)) %>%
  ggplot(aes(plus4s, p)) +
  geom_bar(stat = "identity", fill = "lightgrey", color = "black") +
  scale_y_continuous(name = "% of games",
                     labels = scales::percent,
                     breaks = seq(0, 1, by = .05)) +
  scale_x_continuous(name = "Number of +4s in the game",
                     breaks = 0:5) +
  theme_light(base_size = 15)

# proportion of games with at least 1 plus4
d %>%
  group_by(replicate_id) %>%
  summarise(plus4s = sum(plus4s)) %>%
  summarise(mean(plus4s > 0)) %>%
  pull()

# same proportion by player
d %>%
  group_by(player) %>%
  summarise(prop_had_plus4 = mean(plus4s > 0))

# games with at least 1 plus4
d_plus4 = d %>%
  group_by(replicate_id) %>%
  filter(sum(plus4s) > 0) %>%
  ungroup()

# same proportion by player, given that the game had at least 1 plus4
d_plus4 %>%
  group_by(player) %>%
  summarise(prop_had_plus4 = mean(plus4s > 0))

# proportion of games where the winner has the maximum number of plus4s
d_plus4 %>%
  group_by(replicate_id) %>%
  mutate(max_plus4s = max(plus4s)) %>%
  ungroup() %>%
  filter(winner) %>%
  summarise(mean(plus4s == max_plus4s)) %>%
  pull() %>%
  scales::percent(.01)

# proportion of games where the winner has at least 1 plus4
d_plus4 %>%
  filter(winner) %>%
  summarise(mean(plus4s > 0)) %>%
  pull() %>%
  scales::percent(.01)

# proportion of games where the next neighbor of someone who has a plus4 wins
game_winners = d_plus4 %>%
  filter(winner) %>%
  distinct(replicate_id, winner = player)

d_plus4 %>%
  filter(plus4s > 0) %>%
  group_by(replicate_id) %>%
  summarise(neighbors = paste((as.numeric(player) + 1) %% 4, collapse = ",")) %>%
  inner_join(game_winners, by = "replicate_id") %>%
  summarise(mean(str_detect(neighbors, winner))) %>%
  pull() %>%
  scales::percent(.01)









