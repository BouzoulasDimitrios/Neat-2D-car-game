#! python3

import pygame
import math
import pygame.mask
import random

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
        self.color = GREEN
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

        for end_coordinate in end_cooridnates:

            colission = self.check_collision(start_coorinate, end_coordinate, obstacles)
            if colission is not None:
                pygame.draw.line(screen, (0, 255, 0), start_coorinate, colission)
                colissions.append(int(math.dist(start_coorinate, colission)))
            else:
                pygame.draw.line(screen, (0, 255, 0), start_coorinate, end_coordinate)
                colissions.append(None)

        return colissions

    def move_left(self):
        self.x -= 1
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    
    def move_right(self):
        self.x += 1
        self.rect = self.image.get_rect(center = (self.x, self.y))


    def check_collision(self, start, end, obstacles):
        x1, y1 = start
        x2, y2 = end

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

            # Check for overlap with each obstacle
            for obstacle in obstacles:
                if obstacle.rect.collidepoint(x, y):
                    return int(x), int(y)  # Return the overlapping coordinates
                
        return end  # No overlap found
    
    # def __del__(self) -> None:
    #     print('was deleted')


# Rectangle class
class car(pygame.sprite.Sprite):
    def __init__(self, x, y = -40):
        super().__init__()
        self.image = car_image
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(x, y))
        self.color = RED

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
    
    for i in range(len(waves)):
        waves[i] += randomNum

    car_wave = []

    for x_car_coordinate in waves:#waves[random.randint(0, 1)]:
        car_ = car(x_car_coordinate, Ycoordinate)
        car_wave.append(car_)

    return car_wave


def obstacleUpdate(obstacles, score):
    '''
        removes obstacles that are out of view 
    '''
    if(obstacles.sprites()[0].rect.y > 1225):
        del obstacles[:6]
        score += 1
        return obstacles, score
    
    return obstacles, score


def mainLoop():

    main_rect_x = SCREENWIDTH // 1.95
    main_rect_y = SCREENHEIGHT - 50
    
    rightBoundary = sideBoundaries(height = 200, width =4, x = 502, y = 700)
    leftBoundary  = sideBoundaries(height = 200, width =4, x = -2, y = 700)

    ObstacleList = pygame.sprite.Group()
    # ObstacleList = (generate_wave(160) + generate_wave(340)+ generate_wave(520))

    ObstacleList.add(generate_wave(160))
    ObstacleList.add(generate_wave(340))
    ObstacleList.add(generate_wave(520))

    # testSprite = pygame.sprite.Group()
    # testSprite.add(generate_wave())

    clock = pygame.time.Clock()

    cars = pygame.sprite.Group()

    for i in range(30):
        cars.add(Player(main_rect_x, main_rect_y))

    progress = 0
    score = 0
    running = True

    obstaclesAndBoundaries = pygame.sprite.Group()


    # Game loop
    while running:
    
        screen.blit(background, (-50,0))   

        for event in pygame.event.get(): # End Game
            if event.type == pygame.QUIT: running = False

        # # generate new wave of obstacles
        # if ObstacleList[len(ObstacleList) - 1].rect.y > 160: 
        #     ObstacleList.extend(generate_wave())

        # generate new wave of obstacles
        if ObstacleList.sprites()[-1].rect.y > 160: 
            ObstacleList.add(generate_wave())

        for obstacle in ObstacleList:
            obstacle.move_down()
            # screen.blit(obstacle.image, obstacle.rect)
        
        progress += 0.001
        ObstacleList.draw(screen)


        # obstaclesAndBoundaries = [rightBoundary, leftBoundary] + ObstacleList
        # obstaclesAndBoundaries = pygame.sprite.Group()
        # obstaclesAndBoundaries = obstaclesAndBoundaries.add(ObstacleList)
        # obstaclesAndBoundaries = obstaclesAndBoundaries.add(    rightBoundary   )
        # obstaclesAndBoundaries = obstaclesAndBoundaries.add(    leftBoundary    )


        #draw main 
        for car in cars:

            # car.sensorData = car.get_collision(obstaclesAndBoundaries)

            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_LEFT:
                    car.move_left()
                
                if event.key == pygame.K_RIGHT:
                    car.move_right()

            # for obstacle in obstaclesAndBoundaries: # end game for colission
            #     if car.rect.colliderect(obstacle.rect): 
            #         running = False



        cars.draw(screen)

        txt = f"distance =  {progress}"
        text_ = font.render(txt, True, WHITE)
        screen.blit(text_, (10, 60))

        # check for colission
        ObstacleList, score = obstacleUpdate(ObstacleList, score)

        # Update the display
        pygame.display.flip()
        clock.tick(30)        

    return 

if __name__ == '__main__':
    mainLoop()    
    pygame.quit()
