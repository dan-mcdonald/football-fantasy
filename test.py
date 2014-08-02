#!/usr/bin/env python

import unittest
import ffdraft
from nfldb.types import Enums, PlayPlayer
player_pos = Enums.player_pos

class MockStats(PlayPlayer):
  def __init__(self):
    self.play_players = 0
    self.fumbles_lost = 0
    self.passing_int = 0
    self.passing_tds = 0
    self.passing_twoptm = 0
    self.passing_yds = 0
    self.receiving_twoptm = 0
    self.rushing_tds = 0
    self.rushing_twoptm = 0
    self.rushing_yds = 0

class MockPlayer(object):
  def __init__(self, position):
    self.position = position

class TestScore(unittest.TestCase):
  def setUp(self):
    self.stats = [MockStats()]
    self.qb = MockPlayer(player_pos.QB)

  def test_nothing(self):
    self.assertEqual(ffdraft.player_game_score(self.qb, self.stats, self.stats[0]), 0)

  def test_qb_passing_one_less(self):
    self.stats[0].passing_yds = 74
    self.assertEqual(ffdraft.player_game_score(self.qb, self.stats, self.stats[0]), 2)

  def test_qb_passing_exact(self):
    self.stats[0].passing_yds = 75
    self.assertEqual(ffdraft.player_game_score(self.qb, self.stats, self.stats[0]), 3)

  def test_qb_passing_one_over(self):
    self.stats[0].passing_yds = 76
    self.assertEqual(ffdraft.player_game_score(self.qb, self.stats, self.stats[0]), 3)

  def test_qb_passing_bonus_400(self):
    self.stats[0].passing_yds = 452
    self.assertEqual(ffdraft.player_game_score(self.qb, self.stats, self.stats[0]), 23)

  def test_qb_passing_bonus_300(self):
    self.stats[0].passing_yds = 395
    self.assertEqual(ffdraft.player_game_score(self.qb, self.stats, self.stats[0]), 17)

  def test_qb_tds(self):
    self.stats[0].passing_tds = 3
    self.stats[0].rushing_tds = 1
    self.assertEqual(ffdraft.player_game_score(self.qb, self.stats, self.stats[0]), 24)

  def test_qb_ints(self):
    self.stats[0].passing_int = 2
    self.stats[0].fumbles_lost = 5
    self.assertEqual(ffdraft.player_game_score(self.qb, self.stats, self.stats[0]), -14)

if __name__ == '__main__':
  unittest.main()
