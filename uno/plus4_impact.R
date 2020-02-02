library(dplyr)
library(tidyr)
library(readr)
library(ggplot2)

d = read_csv("plus4_impact.csv") %>%
  gather("player", "plus4s", -winner, -replicate_id) %>%
  mutate(player = substr(player, 8, 8)) %>%
  mutate(winner = player == as.character(winner)) %>%
  arrange(replicate_id, player)

# proportion of games with at least 1 plus4
d %>%
  group_by(replicate_id) %>%
  summarise(plus4s = sum(plus4s)) %>%
  summarise(mean(plus4s > 0)) %>%
  pull()

# same proportion by player
d %>%
  group_by(player) %>%
  summarise(prop_had_plus4 = mean(plus4s > 0)) %>%
  ggplot(aes(player, prop_had_plus4)) +
  geom_bar(stat = "identity", fill = "light grey") +
  geom_hline(yintercept = .3, lty = 2, lwd = 1) +
  scale_y_continuous(name = "% of games with at least 1 plus 4",
                     labels = scales::percent) +
  scale_x_discrete(name = "Player") +
  coord_flip() +
  theme_bw(base_size = 15)

# games with at least 1 plus4
d_plus4 = d %>%
  group_by(replicate_id) %>%
  filter(sum(plus4s) > 0) %>%
  ungroup()

# same proportion by player, given that the game had at least 1 plus4
d %>%
  group_by(player) %>%
  summarise(prop_had_plus4 = mean(plus4s > 0)) %>%
  ggplot(aes(player, prop_had_plus4)) +
  geom_bar(stat = "identity", fill = "light grey") +
  geom_hline(yintercept = .3, lty = 2, lwd = 1) +
  scale_y_continuous(name = "% of games with at least 1 plus 4",
                     labels = scales::percent) +
  scale_x_discrete(name = "Player") +
  coord_flip() +
  theme_bw(base_size = 15)

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
d_plus4 %>%
  filter(winner) %>%
  summarise(mean(plus4s > 0)) %>%
  pull() %>%
  scales::percent(.01)

