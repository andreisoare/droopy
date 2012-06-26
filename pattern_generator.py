# -*- coding: latin -*-

# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)

import random
import itertools
import operator
import string
import re
import logging

import global_settings

GET_NUMBER = 5
UPPER_LIMIT = 4
CYCLE_TIMEOUT = 25

class PatternGenerator:
  @staticmethod
  def generate(email_address, display_name, unames, get_number=GET_NUMBER):
    try:
      email_username = email_address[0:email_address.find('@')]
    except:
      logging.warn('Error! Email missing!')
      return []

    try:
      display_name = display_name.encode('ascii', 'ignore').lower()
    except:
      logging.warn('Could not encode display name %s' % display_name)
      return []

    if display_name == '':
      return list(set(unames + [email_username]))

    display_names = re.findall(r'\w+', display_name)
    display_names = list(set(display_names))

    importance_dict = {}
    for display_name in display_names:
      importance_dict[display_name] = 1 if \
        string.find(email_username, display_name) >= 0 else -1

    score_dict = {}

    # truncate if more than 3 names
    if len(display_names) > 3:
      display_names = display_names[0:2] + display_names[-1:]

    if len(display_names) == 0:
      return list(set(unames + [email_username]))

    elif len(display_names) == 1:
      return list(set(unames + display_names + [email_username]))

    elif len(display_names) == 2:
      permutations = list(set(list(itertools.permutations(display_names))))
      score_dict = PatternGenerator.bigenerate(permutations, importance_dict)

    elif len(display_names) == 3:
      # generate 3-element pairs
      permutations = list(set(list(itertools.permutations(display_names))))
      dict3 = PatternGenerator.trigenerate(permutations, importance_dict)

      # generate 2-length combinations
      combinations = list(set(list(itertools.combinations(display_names, 2))))
      permutations = []
      for combination in combinations:
        permutations.extend(list(itertools.permutations(list(combination))))
      permutations = list(set(permutations))
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

    step_count = 0
    if len(result_x) < UPPER_LIMIT:
      while len(result_x) < GET_NUMBER:
        if step_count > CYCLE_TIMEOUT:
          result_x = list(set(result_x + [(email_username, best_score)]))
          break
        step_count += 1
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
  #email = 'diana.tiriplica@gmail.com'
  #display_name  = 'Diana-Victoria Tiriplica'
  #p = PatternGenerator.generate(email, display_name, [\
  #                'diana_tiriplica', 'diana.tiriplica', 'dtiriplica'])
  #p = PatternGenerator.generate(email, display_name, [])
  #p = PatternGenerator.generate('infoasg@yahoo.com', 'S S', ['infoasg'])
  #p = PatternGenerator.generate('camp101988@yahoo.com', 'Mihai-Taba Viorel.', [])
  #p = PatternGenerator.generate('camp101988@yahoo.com', 'Mihai-Tabara V.', [])
  #print 'Final'
  #print p
