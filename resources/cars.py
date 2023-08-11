import pygame
import math
import numba

carWidth = 30  
carHeight = 50  

car_image = pygame.image.load("./resources/obstacleCar.png") 
car_image = pygame.transform.scale(car_image, (carWidth, carHeight))

mainCarImage = pygame.image.load("./resources/mainCar.png") 
mainCarImage = pygame.transform.scale(mainCarImage, (carWidth, carHeight))


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


    def get_collision(self, obstacles, screen):

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
        self.x -= 1
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    
    def move_right(self):
        self.x += 1
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