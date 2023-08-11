#! python3

import time

from resources.cars import sideBoundaries, car, Player

import pygame
import pygame.mask
import random

# neat
import neat
import numpy as np
import os

# Initialize Pygame
pygame.init()

# Set up the display
SCREENWIDTH, SCREENHEIGHT = 500, 800
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Distance Sensor Demo")

background = pygame.image.load('./resources/road.png')
background = pygame.transform.scale(background, (600, 1000))


# Color definition
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)

carWidth = 30  
carHeight = 50  

font = pygame.font.Font(None, 24)


def generate_wave(Ycoordinate = -40):
    '''
        returns a list containing 4 car objects the are on the same height and different Xs
        the car objects are spaced out with a minimal space distance
    
    '''

    randomNum = random.randint(0,60)
    waves = [20, 100, 180, 260, 340, 420, 500]
    car_wave = []

    for i in range(len(waves)): waves[i] += randomNum

    for x_car_coordinate in waves:
        car_ = car(x_car_coordinate, Ycoordinate)
        car_wave.append(car_)

    return car_wave


def obstacleUpdate(obstacles):
    '''
        removes obstacles that are out of view 
    '''

    if(obstacles.sprites()[0].rect.y > 1050): 
        for i in obstacles.sprites()[:6]: i.kill()

    return 


def mainLoop(genomes, config):
        
    maxDistances = [281, 331, 409, 409, 331, 281]    
    obstaclesAndBoundaries = pygame.sprite.Group()
    cars = pygame.sprite.Group()
    clock = pygame.time.Clock()
    alive = []  
    nets = []
    ge = []

    running = True
    progress = 0

    main_rect_x = SCREENWIDTH // 1.95
    main_rect_y = SCREENHEIGHT - 50
    
    rightBoundary = sideBoundaries(height = 200, width =4, x = 502, y = 700)
    leftBoundary  = sideBoundaries(height = 200, width =4, x = -2, y = 700)

    ObstacleList = pygame.sprite.Group()
    ObstacleList.add(generate_wave(160))
    ObstacleList.add(generate_wave(340))
    ObstacleList.add(generate_wave(520))

    for id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        cars.add(Player(main_rect_x, main_rect_y))    
        ge.append(genome)
        alive.append(True)

    time.sleep(15)

    # Game loop
    while running:
    
        screen.blit(background, (-50,0))   

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: running = False

        # generate new wave of obstacles
        if ObstacleList.sprites()[-1].rect.y > 160: ObstacleList.add(generate_wave())

        # move obstacle cars down
        for obstacle in ObstacleList: obstacle.move_down()
        
        progress += 0.001
        ObstacleList.draw(screen)

        obstaclesAndBoundaries.add(rightBoundary)
        obstaclesAndBoundaries.add(leftBoundary)
        obstaclesAndBoundaries.add(ObstacleList)

        running = False

        for x, car in enumerate(cars):

            ge[x].fitness = progress 

            car.sensorData = car.get_collision(obstaclesAndBoundaries, screen)
            values = list(car.sensorData)

            # values normalization
            for i, v in enumerate(values): values[i] = v/maxDistances[i]

            # move car based on genome output
            output = nets[x].activate(values)
            movement = np.argmax(output)
            if movement == 0: car.move_left()
            elif movement == 2: car.move_right() 

            for obstacle in obstaclesAndBoundaries.sprites(): 
                running = True
                if car.rect.colliderect(obstacle.rect):  alive[x] = False

            # # single player mode 
            # car.sensorData = car.get_collision(obstaclesAndBoundaries.sprites(), screen)
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT: car.move_left()
            #     if event.key == pygame.K_RIGHT: car.move_right()

        
        # remove crashed cars
        for x in reversed(range(0, len(alive))):
            if not alive[x]:
                del alive[x]
                cars.sprites()[x].kill()
                del ge[x]
                del nets[x]

        cars.draw(screen)

        txt = "distance =  %.3f alive = %.0f" %(progress, len(alive))
        text_ = font.render(txt, True, WHITE)
        screen.blit(text_, (10, 60))

        obstacleUpdate(ObstacleList)

        # Update the display
        pygame.display.flip()
        clock.tick(60)        

    return 

def run_neat(config_file):

    # Load configuration.
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)
    p = neat.Checkpointer.restore_checkpoint('./resources/neat-checkpoint-370')

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10))

    winner = p.run(mainLoop, 100000)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)



if __name__ == '__main__': 
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, './resources/config.txt')
    run_neat(config_path)
    pygame.quit()
    
