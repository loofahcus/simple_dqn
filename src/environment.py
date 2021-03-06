import sys
import os
import logging
import cv2
logger = logging.getLogger(__name__)

class Environment:
  def __init__(self):
    pass

  def numActions(self):
    # Returns number of actions
    raise NotImplementedError

  def restart(self):
    # Restarts environment
    raise NotImplementedError

  def act(self, action):
    # Performs action and returns reward
    raise NotImplementedError

  def getScreen(self):
    # Gets current game screen
    raise NotImplementedError

  def isTerminal(self):
    # Returns if game is done
    raise NotImplementedError

class ALEEnvironment(Environment):
  def __init__(self, rom_file, args):
    from ale_python_interface import ALEInterface
    self.ale = ALEInterface()
    if args.display_screen:
      if sys.platform == 'darwin':
        import pygame
        pygame.init()
        self.ale.setBool(b'sound', False) # Sound doesn't work on OSX
      elif sys.platform.startswith('linux'):
        self.ale.setBool(b'sound', True)
      self.ale.setBool(b'display_screen', True)

    self.ale.setInt(b'frame_skip', args.frame_skip)
    self.ale.setFloat(b'repeat_action_probability', args.repeat_action_probability)
    self.ale.setBool(b'color_averaging', args.color_averaging)

    if args.random_seed:
      self.ale.setInt(b'random_seed', args.random_seed)

    if args.record_screen_path:
      if not os.path.exists(args.record_screen_path):
        logger.info(b"Creating folder %s" % args.record_screen_path)
        os.makedirs(args.record_screen_path)
      logger.info(b"Recording screens to %s", args.record_screen_path)
      self.ale.setString(b'record_screen_dir', args.record_screen_path)

    if args.record_sound_filename:
      logger.info(b"Recording sound to %s", args.record_sound_filename)
      self.ale.setBool(b'sound', True)
      self.ale.setString(b'record_sound_filename', args.record_sound_filename)

    self.ale.loadROM(str.encode(rom_file))

    if args.minimal_action_set:
      self.actions = self.ale.getMinimalActionSet()
      logger.info("Using minimal action set with size %d" % len(self.actions))
    else:
      self.actions = self.ale.getLegalActionSet()
      logger.info("Using full action set with size %d" % len(self.actions))
    logger.debug("Actions: " + str(self.actions))

    self.screen_width = args.screen_width
    self.screen_height = args.screen_height

  def numActions(self):
    return len(self.actions)

  def restart(self):
    self.ale.reset_game()

  def act(self, action):
    reward = self.ale.act(self.actions[action])
    return reward

  def getScreen(self):
    screen = self.ale.getScreenGrayscale()
    resized = cv2.resize(screen, (self.screen_width, self.screen_height))
    return resized

  def isTerminal(self):
    return self.ale.game_over()

class GymEnvironment(Environment):
  # For use with Open AI Gym Environment
  def __init__(self, env_id, args):
    import gym
    self.gym = gym.make(env_id)
    self.obs = None
    self.terminal = None

    self.screen_width = args.screen_width
    self.screen_height = args.screen_height

  def numActions(self):
    import gym
    assert isinstance(self.gym.action_space, gym.spaces.Discrete)
    return self.gym.action_space.n

  def restart(self):
    self.obs = self.gym.reset()
    self.terminal = False

  def act(self, action):
    self.obs, reward, self.terminal, _ = self.gym.step(action)
    return reward

  def getScreen(self):
    assert self.obs is not None
    return cv2.resize(cv2.cvtColor(self.obs, cv2.COLOR_RGB2GRAY), (self.screen_width, self.screen_height))

  def isTerminal(self):
    assert self.terminal is not None
    return self.terminal
