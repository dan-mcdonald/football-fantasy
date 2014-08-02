from __future__ import division
import nfldb
from nfldb import aggregate
import nfldb.types
from nfldb.types import Enums
player_pos = Enums.player_pos
from itertools import groupby

db = nfldb.connect()

def def_score(team, game_plays, stats):
  pts_total = 0

  # 1 point for every sack
  # TODO find out how half-sacks count, for now they are just 1/2 point
  pts_total += 1 * stats.defense_sk

  # 2 points for every fumble recovery
  pts_total += 2 * stats.defense_frec

  # 2 points for every interception
  pts_total += 2 * stats.defense_int

  # 1 point for every 10 yards an interception is returned
  pts_total += stats.defense_frec_yds // 10

  # 6 points for every return touchdown
  pts_total += 6 * (stats.kickret_tds + stats.puntret_tds)

  # 6 points for defensive touchdowns
  pts_total += 6 * stats.defense_tds

  # 1 point for every 25 yards of combined return yardage from punts and kickoffs
  pts_total += (stats.puntret_yds + stats.kickret_yds) // 25

  return pts_total

def qb_score(player, game_plays, stats):
  pts_total = 0

  # Players scoring or throwing a 2 point conversion = 2 points
  pts_2pconv = 2 * (stats.rushing_twoptm + stats.passing_twoptm + stats.receiving_twoptm)

  # 1 point for every 25 yards passing
  pts_total += stats.passing_yds // 25

  if stats.passing_yds >= 400:
    # 5 points for 400 yards passing (bonus)
    pts_total += 5
  elif stats.passing_yds >= 300:
    # 2 points for 300 yards passing (bonus)
    pts_total += 2

  # 1 point for every 10 yards rushing
  pts_total += stats.rushing_yds // 10

  # 6 points for throwing/rushing touchdown
  pts_total += 6 * (stats.passing_tds + stats.rushing_tds)

  # -2 points for interceptions & fumbles lost (penalty)
  pts_total += -2 * (stats.passing_int + stats.fumbles_lost)
  return pts_total

def kicker_score(player, game_plays, stats):
  pts_total = 0
  for play in game_plays:
    # 3 points for all field goals 1-49 yards
    if play.kicking_fgm_yds < 50:
      pts_total += 3
    # 5 points for all field goals 50 yards and over
    else:
      pts_total += 5

  # 1 point for all extra points
  pts_total += 1 * stats.kicking_xpmade

  # -3 points for a missed field goal
  pts_total += -3 * stats.kicking_xpmissed

  return pts_total

def wr_te_score(player, game_plays, stats):
  pts_total = 0

  # Players scoring or throwing a 2 point conversion = 2 points
  pts_2pconv = 2 * (stats.rushing_twoptm + stats.passing_twoptm + stats.receiving_twoptm)

  # 1 point for every 10 yards receiving/rushing (reverses, etc)
  pts_total += stats.rushing_yds // 10

  if stats.rushing_yds >= 200:
    # 5 points for 200 yards receiving (bonus)
    pts_total += 5
  elif stats.rushing_yds >= 100:
    # 2 points for 100 yards receiving (bonus)
    pts_total += 2

  # 1 point for every reception
  pts_total += 1 * stats.receiving_rec

  # 6 points for every touchdown receiving/rushing
  pts_total += 6 * (stats.receiving_tds + stats.rushing_tds)

  # -2 points for fumbles lost (penalty)
  pts_total += -2 * stats.fumbles_lost

  return pts_total

# def player_game_score(player, game_plays, stats):
#   assert player.position != player_pos.UNK
#   if player.position in [player_pos.DB, player_pos.P, player_pos.FS, player_pos.SS, player_pos.SAF, player_pos.OLB, player_pos.DE, player_pos.LB, player_pos.DT, player_pos.CB, player_pos.G, player_pos.MLB, player_pos.ILB, player_pos.NT, player_pos.OT]:
#     return def_score(player, game_plays, stats)
#   elif player.position in [player_pos.QB, player_pos.WR, player_pos.TE, player_pos.T, player_pos.RB, player_pos.FB, player_pos.OG]:
#     return off_score(player, game_plays, stats)
#   elif player.position == player_pos.K:
#     return kicker_score(player, game_plays, stats)
#   elif player.position in [player_pos.LS, player_pos.C]:
#     return None
#   else:
#     raise Exception("What type of player is "+str(player.position)+"?")

def player_rank(player, score_func):
  #print "Ranking for", player.position, player.full_name

  player_games = nfldb.Query(db)
  player_games.game(season_year=2013, season_type='Regular').sort(('week', 'asc'))
  player_games.player(player_id=player.player_id)
  total = 0
  count = 0
  for game in player_games.as_games():
    game_pps = nfldb.Query(db).game(gsis_id=game.gsis_id).player(player_id=player.player_id).as_play_players()
    stats = aggregate(game_pps)[0]
    score = score_func(player, game_pps, stats)
    if score is not None:
      total += score
      count += 1
  if count == 0:
    return None
  else:
    avg = total / count
    return avg

def team_rank(team, score_func):
  team_games = nfldb.Query(db)
  team_games.game(season_year=2013, season_type='Regular').sort(('week', 'asc'))
  team_games.team(team_id=team.team_id)
  total = 0
  count = 0
  for game in team_games.as_games():
    game_pps = nfldb.Query(db).game(gsis_id=game.gsis_id).team(team_id=team.team_id).as_play_players()
    stats = aggregate(game_pps)
    score = score_func(team, game_pps, stats)
    if score is not None:
      total += score
      count += 1
  if count == 0:
    return None
  else:
    return total / count

if __name__ == '__main__':
  q = nfldb.Query(db)
  defteams = []
  for dteam in q.game(season_year=2013, season_type='Regular').as_teams():
    defteams.append((dteam, team_rank(dteam, def_score)))
  defteams.sort(key=lambda pair: pair[1], reverse=True)
  for pair in defteams:
    print pair[0], pair[1]

  # qbs = []
  # for qb in q.game(season_year=2013, season_type='Regular').player(position=player_pos.QB).as_players():
  #   qbs.append((qb, player_rank(qb, qb_score)))
  # qbs.sort(key=lambda pair: pair[1], reverse=True)
  # for pair in qbs:
  #   print pair[0], pair[1]
