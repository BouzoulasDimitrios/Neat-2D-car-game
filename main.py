#! python3

import pygame
import math
import pygame.mask
import random
import numba 

# neat
import neat
import numpy as np
import os

# debugging
import cProfile

# Initialize Pygame
pygame.init()

# Set up the display
SCREENWIDTH, SCREENHEIGHT = 500, 800
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Distance Sensor Demo")

background = pygame.image.load('./road.png')
background = pygame.transform.scale(background, (600, 1000))


# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)

carWidth = 30  
carHeight = 50  

car_image = pygame.image.load("./obstacleCar.png") 
car_image = pygame.transform.scale(car_image, (carWidth, carHeight))

mainCarImage = pygame.image.load("./mainCar.png") 
mainCarImage = pygame.transform.scale(mainCarImage, (carWidth, carHeight))

font = pygame.font.Font(None, 24)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image = mainCarImage
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(x, y))
        self.sensorData = []


    def get_collision(self, obstacles):

        self.rect.centerx
        self.rect.centery
            
        start_coorinate = [self.rect.centerx, self.rect.centery + 25]

        end_cooridnates = [
                            [self.rect.centerx - 280, self.rect.centery  ],\

                            [self.rect.centerx - 90 , self.rect.centery - 294],\

                            [self.rect.centerx - 15 , self.rect.centery - 384],\
                                                        
                            [self.rect.centerx + 15 , self.rect.centery - 384],\

                            [self.rect.centerx + 90 , self.rect.centery - 294],\

                            [self.rect.centerx + 280, self.rect.centery  ],\
                          ]
        
        colissions = []

        obstacle_coords = [(obstacle.rect.centerx, obstacle.rect.centery) for obstacle in obstacles]

        for end_coordinate in end_cooridnates:
            
            x1, y1 = start_coorinate
            x2, y2 = end_coordinate
    
            colission = self.check_collision(x1= int(x1), x2= int(x2), y1= int(y1), y2= int(y2), obstacles= obstacle_coords)#, obstacles = obstacles)

            if colission is not None:
                pygame.draw.line(screen, (0, 255, 0), start_coorinate, colission)
                colissions.append(int(math.dist(start_coorinate, colission)))
            else:
                pygame.draw.line(screen, (0, 255, 0), start_coorinate, end_coordinate)
                colissions.append(None)

        return colissions

    def move_left(self):
        self.x -= 2
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    
    def move_right(self):
        self.x += 2
        self.rect = self.image.get_rect(center = (self.x, self.y))

    @staticmethod
    @numba.jit(nopython = True)    
    def check_collision(x1, y1, x2, y2, obstacles):

        dx = x2 - x1
        dy = y2 - y1

        # Calculate the number of steps in x and y directions
        num_steps = max(abs(dx), abs(dy))

        # Calculate the step size for x and y directions
        step_x = dx / num_steps
        step_y = dy / num_steps

        # Iterate along the line from start to end coordinates
        for i in range(int(num_steps+1)):
            x = x1 + i * step_x
            y = y1 + i * step_y
                
            for obstacle_x, obstacle_y in obstacles:
                if obstacle_x - 15 <= x <= obstacle_x + 15 and obstacle_y - 25 <= y <= obstacle_y + 25:
                    return int(x), int(y)  # Return the overlapping coordinates

        return x2, y2 # No overlap found


# Rectangle class
class car(pygame.sprite.Sprite):
    def __init__(self, x, y = -40):
        super().__init__()
        self.image = car_image
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(x, y))

    def move_down(self):
        self.y += 2
        self.rect = self.image.get_rect(center = (self.x, self.y))
    
    # def __del__(self) -> None:
    #     print('was deleted')


class sideBoundaries(car):
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.x = x
        self.y = y
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect(center=(x, y))


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

            car.sensorData = car.get_collision(obstaclesAndBoundaries)
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
                    # continue

            # # single player mode 
            # car.sensorData = car.get_collision(obstaclesAndBoundaries.sprites()[:36])
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

        txt = f"distance =  {progress}"
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
    p = neat.Checkpointer.restore_checkpoint('./neat-checkpoint-370')

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
    config_path = os.path.join(local_dir, './config.txt')
    run_neat(config_path)
    # cProfile.run('mainLoop()') # used for debugging
    pygame.quit()
    
