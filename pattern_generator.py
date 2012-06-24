# -*- coding: latin -*-

# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)
# TODO(mihai): What happens when unsufficient profiles yields the first group ?

import random
import itertools
import operator
import string
import re

GET_NUMBER = 5
UPPER_LIMIT = 4

class PatternGenerator:
  @staticmethod
  def generate(email_address, display_name, unames, get_number=GET_NUMBER):
    email_username = email_address[0:email_address.find('@')]
    display_name = str(unicode(display_name, errors='ignore')).lower()

    if display_name == '':
      return list(set(unames + [email_username]))

    display_names = re.findall(r'\w+', display_name)

    importance_dict = {}
    for display_name in display_names:
      importance_dict[display_name] = 1 if \
        string.find(email_username, display_name) >= 0 else -1

    score_dict = {}

    # truncate if more than 3 names
    if len(display_names) > 3:
      display_names = display_names[0:2] + display_names[-1:]

    if len(display_names) == 0:
      return unames

    elif len(display_names) == 1:
      return list(set(unames + display_names))

    elif len(display_names) == 2:
      permutations = list(itertools.permutations(display_names))
      score_dict = PatternGenerator.bigenerate(permutations, importance_dict)

    elif len(display_names) == 3:
      # generate 3-element pairs
      permutations = list(itertools.permutations(display_names))
      dict3 = PatternGenerator.trigenerate(permutations, importance_dict)

      # generate 2-length combinations
      combinations = list(itertools.combinations(display_names, 2))
      permutations = []
      for combination in combinations:
        permutations.extend(list(itertools.permutations(list(combination))))
      dict2 = PatternGenerator.bigenerate(permutations, importance_dict)
      score_dict = dict(dict2.items() + dict3.items())

    # chose random sample from best chunk of usernames
    sorted_x = sorted(score_dict.iteritems(), key=operator.itemgetter(1), \
                reverse=True)
    group_x = itertools.groupby(sorted_x, operator.itemgetter(1))
    for key, group in group_x:
      interest_x = (list(group))
      best_score = key
      break

    result_x = [(uname, best_score) for uname in unames]

    if len(result_x) < UPPER_LIMIT:
      while len(result_x) < GET_NUMBER:
        try:
          random_pick = random.choice(interest_x)
        except IndexError:
          print 'Error! Empty set give here'
          continue
        if random_pick not in result_x:
          result_x.append(random_pick)

    return [tuplu[0] for tuplu in result_x]

  @staticmethod
  def bigenerate(permutations, value_dict):
    return_dict = {}

    for mytuple in permutations:
      score = sum(value_dict[name] for name in mytuple)
      sign_list = ['', '.', '_']
      for sign in sign_list:
        new_pattern = sign.join(name for name in mytuple)
        return_dict[new_pattern] = score

      pos_list = [(0,1), (1,0)]
      for pos in pos_list:
        new_pattern = ''.join([mytuple[pos[0]][0], mytuple[pos[1]]])
        return_dict[new_pattern] = score

    return return_dict

  @staticmethod
  def trigenerate(permutations, value_dict):
    return_dict = {}

    for mytuple in permutations:
      score = sum(value_dict[name] for name in mytuple)
      sign_list = ['', '.', '_']
      for sign in sign_list:
        new_pattern = sign.join(name for name in mytuple)
        return_dict[new_pattern] = score

      new_pattern = ''.join([mytuple[0][0], mytuple[1][0], mytuple[2]])
      return_dict[new_pattern] = score

    return return_dict

#if __name__=="__main__":
#  email = 'diana.tiriplica@gmail.com'
#  display_name  = 'Diana-Victoria Tiriplica'
#  p = PatternGenerator.generate(email, display_name, [\
#                  'diana_tiriplica', 'diana.tiriplica', 'dtiriplica'])
#  print 'Final'
#  print p
