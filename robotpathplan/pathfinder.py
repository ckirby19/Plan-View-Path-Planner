import math
import numpy as np

class PathFinder:
    def __init__(self,start: tuple, goal: tuple, canvas: tuple, obstacles: list) :
        """
        Initialise path planning with start,goal,canvas,list of obstacles and resolution of grid

        start: (X,Y) in pixels
        goal: (X,Y) in pixels
        canvas: (X,Y) in pixels. Origin in top left, with +X right, +Y down
        resolution: Grid Resolution pixels per length 
        obstacles: list of obstacles
        """
        # TODO: Get rid of this discrete version, stick with the continuous problem, and for each line within some 
        # box around 
        print("Started Path Planning...")
        self.startX,self.startY = start
        self.goalX,self.goalY = goal
        self.width,self.height = canvas
        self.obs = obstacles
        self.res = 1 #higher number, lower resolution (less cells in grid)

        self.gridX = round(self.width/self.res)
        self.gridY = round(self.height/self.res)
        print("Grid size of",(self.gridX,self.gridY))

        # motion expressed as dx,dy (units of grid motion),cost of move
        self.motion = [[1, 0, 1],
                  [0, 1, 1],
                  [-1, 0, 1],
                  [0, -1, 1]]
                #   [-1, -1, round(math.sqrt(2),3)],
                #   [-1, 1, round(math.sqrt(2),3)],
                #   [1, -1, round(math.sqrt(2),3)],
                #   [1, 1, round(math.sqrt(2),3)]]

        # obstacle map generation
        self.obstacleMap = [[0 for i in range(self.gridX)] for j in range(self.gridY)]
        self.createObstacleMap()

    def createObstacleMap(self):
        for obstacle in self.obs:
            if obstacle["type"] == "line":
                self.obstacleFromLine(obstacle)
    
    def convertPos(self,x,y):
        # Convert from pixel space to grid space

        # Ratio of self.gridX/self.width = indX/x
        indX = round(x*self.gridX/self.width)
        indY = round(y*self.gridY/self.height)
        return (indX,indY)

    def convertLength(self,pixelLength):
        # Convert length from pixel space to grid space
        return math.ceil(pixelLength/self.res)

    def obstacleFromLine(self,line):
        # Given end points of line, create a bounding box around the line, accounting for the rotation of each element
        #y1 and y2 tell us orientation of line. If y1 > y2, then line is rotated s.t left side is lower. If y2 > y1, right side if lower
        x1, y1 = line["left"] + line["x1"],line["top"] + line["y1"] 
        x2, y2 = line["left"] + line["x2"],line["top"] + line["y2"]
        print("Line details",x1,y1,x2,y2)
        # x1,y1 = self.convertPos(x1,y1)
        # x2,y2 = self.convertPos(x1,y1)
        x1,y1 = round(x1/self.res), round(y1/self.res)
        x2,y2 = round(x2/self.res), round(y2/self.res)
        
        print("After conversion",x1,y1,x2,y2)
        gradient = (y2 - y1)/(x2 - x1)
        intersept = y1 - gradient*x1
        perpGradient = -1/gradient
        if x1 == x2:
            #Vertical line
            pass
        elif y1 == y2:
            #Horizontal line
            pass
        else:
            minX = min(x1,x2)
            maxX = max(x1,x2)
            for middleX in range(minX,maxX):
                middleY = round(gradient*middleX + intersept)
                print("X Y values:",middleX,middleY)
                for w in range(0,int(line["strokeWidth"])//2):
                    try:
                        print("width",round(middleX + w),round(middleY + w*perpGradient))
                        self.obstacleMap[round(middleY + w*perpGradient)][round(middleX + w)] = 1
                        self.obstacleMap[round(middleY - w*perpGradient)][round(middleX - w)] = 1
                    except:
                        continue
            
        
        
        
        
        # lineX1 = line["left"] + line["x1"]
        # lineY1 = line["top"] + line["y1"]
        # lineX2 = line["left"] + line["x2"]
        # lineY2 = line["top"] + line["y2"]
        # minX = min(lineX1,lineX2)
        # maxX = max(lineX1,lineX2)
        # minY = min(lineY1,lineY2)
        # maxY = max(lineY1,lineY2)
        # lineGridMinX,lineGridMinY = self.convertPos(minX,minY)
        # lineGridMaxX,lineGridMaxY = self.convertPos(maxX,maxY)

        # if (lineGridMaxX == lineGridMinX):
        #     for y in range(lineGridMinY,lineGridMaxY):
        #         self.obstacleMap[y][lineGridMaxX-1] = 1
        #         self.obstacleMap[y][lineGridMaxX] = 1
        #         self.obstacleMap[y][lineGridMaxX+1] = 1
        # elif (lineGridMaxY == lineGridMinY):
        #     for x in range(lineGridMinX,lineGridMaxX):
        #         self.obstacleMap[lineGridMaxY-1][x] = 1
        #         self.obstacleMap[lineGridMaxY][x] = 1
        #         self.obstacleMap[lineGridMaxY+1][x] = 1
        # else:
        #     # print(lineGridMinX,lineGridMinY,lineGridMaxX,lineGridMaxY)
        #     numPixels = min(lineGridMaxX-lineGridMinX,lineGridMaxY-lineGridMinY)
        #     # print("Num pixels",numPixels)
        #     x = lineGridMinX
        #     y = lineGridMinY
        #     for i in range(0,numPixels):
        #         self.obstacleMap[y-1][x] = 1
        #         self.obstacleMap[y][x-1] = 1
        #         self.obstacleMap[y][x] = 1
        #         self.obstacleMap[y+1][x] = 1
        #         self.obstacleMap[y][x+1] = 1
        #         x+=1
        #         y+=1
            # gradient = (lineGridMaxY - lineGridMinY)/(lineGridMaxX - lineGridMinX)
            
            # intercept = (lineGridMinY - gradient*lineGridMinX)
            # print(gradient,intercept,lineGridMinX,lineGridMinY,lineGridMaxX,lineGridMaxY)
            # for x in range(lineGridMinX,lineGridMaxX):
            #     y = round(gradient*x + intercept)
            #     self.obstacleMap[y][x] = 1
        # lineThickness = self.convertLength(line["strokeWidth"])

        #original line = y=mx+c where m = y2-y1/(x2-x1)
        #We want 1/m direction so (x2-x1)/(y2-y1). y = (x2-x1)/(y2-y1)*x with each grid point as origin
        #Length = linethickness/2 x^2+y^2 = (lineThickness/2)^2 and y = mx
        # (1+m^2)x^2 = (lineThickness/2)^2 x = sqrt((lineThickness/2)^2/(1+m^2))

        # thicknessAngle = math.tan(lineGridMaxY-lineGridMinY/(lineGridMaxX-lineGridMinX)) + math.pi/2
        # aTanThAngle = math.atan(thicknessAngle)

        
        # thicknessXMax = math.sqrt((lineThickness/2)**2/(1+gradient**2))
        # thicknessXMin = -thicknessXMax
        # thicknessYMax = gradient*thicknessXMax
        # thicknessYMin = -thicknessYMax
        # Also add grid points to represent line thickness. Convert line thickness into grid space length, 
            # and direction is found from the normal of the direction P1 -> P2
        # gridPoints = []
        

                # for thickness in range(lineThickness+1):
                #     #thickness^2 = thX^2 +thY^2
                #     #tan(thY^2/thX^2) = thicknessAngle
                #     # atan(thicknessAngle)*thX^2 = thY^2
                #     # (1+atan(thicknessAngle))*thX^2 = thickness^2
                #     # thX = sqrt((thickness^2)/(1+atan(thicknessAngle)))

                #     thX = math.sqrt(thickness**2/(1+aTanThAngle))
                #     thY = math.sqrt(thickness**2 - thX**2)
                #     gridPoints.append((round(x+thX),round(y+thY)))
                #     if (thX,thY) != (0,0):
                #         gridPoints.append((round(x-thX),round(y-thY)))

    def binaryInsert(self,element,stack,left,right):
        """Binary Insertion of element into stack, descending, based on distance from (distance,current,prev)
        
        Keyword arguments:
        argument -- description
        Return: return_description
        """
        if right <= left:
            return stack[:left] + [element] + stack[left:]
        mid = left + (right-left)//2
        if stack[mid][0] < element[0]:
            #Then we want element to go on left side
            return self.binaryInsert(element,stack,left,mid-1)
        elif stack[mid][0] > element[0]:
            #Then we want element to go on right side
            return self.binaryInsert(element,stack,mid+1,right)
        else:
            return stack[:mid] + [element] + stack[mid:]
        

    def findPath(self):
        """Using Dijkstra's search algorithm
        
        output:
            searchPath: a list of points that were searched, in order
            finalPath: a list of points for the final shortest path to the goal, in order
        """
        # Go in each direction in self.motion, keeping track of cost. 
        # Keep the list of points as they are visited. A greedy approach where we assume that the best next step
            # taken until the end will give the optimal solution at the end
        # At the end, when we have the shortest path (least cost), save all the points taken to get to goal
        # Can add cell if not in visited and not in obstacleMap
        foundGoal = False
        visited = [[0 for i in range(self.gridX)] for j in range(self.gridY)]
        start = self.convertPos(self.startX,self.startY)
        goal = self.convertPos(self.goalX,self.goalY)
        orderOfVisit = [start] #Here we just add the cells as we visit them
        prevNodes = dict() #current:previous
        stack = [(0,start)] # (total distance,cur pos)
        print("Start",start,"Goal",goal)
        while not foundGoal and stack:
            curDistance,curCell = stack.pop()
            for move in self.motion:
                nextX = curCell[0] + move[0]
                nextY = curCell[1] + move[1]
                # print(nextX,self.gridX,nextY,self.gridY)
                if 0 <= nextX < self.gridX and 0 <= nextY < self.gridY:
                    nextCell = (nextX,nextY)
                    if nextCell == goal:
                        prevNodes[goal] = curCell
                        foundGoal = True
                        break
                    if visited[nextCell[1]][nextCell[0]] == 0:
                        #We need to check we are not jumping to a diagonal 
                        if self.obstacleMap[nextCell[1]][nextCell[0]] == 0:
                            visited[nextCell[1]][nextCell[0]] = 1
                            orderOfVisit.append(nextCell)
                            prevNodes[nextCell] = curCell
                            toInsert = (curDistance+move[2],nextCell)
                            stack = self.binaryInsert(toInsert,stack,0,len(stack))
                        
        finalPath = []
        if foundGoal:
            #Then we need to trace back and form our list of points that make up the goal
            currentNode = goal
            while currentNode!=start:
                finalPath.append(currentNode)
                currentNode = prevNodes[currentNode]
            finalPath.append(start)
            finalPath.reverse()
        print("Path found!")
        return orderOfVisit,finalPath

        
    
