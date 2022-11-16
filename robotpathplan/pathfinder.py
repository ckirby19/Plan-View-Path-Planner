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
        self.startX,self.startY = start
        self.goalX,self.goalY = goal
        self.width,self.height = canvas
        self.obs = obstacles
        self.res = 10 #higher number, lower resolution (less cells in grid)

        self.gridX = round(self.width/self.res)
        self.gridY = round(self.height/self.res)

        # motion expressed as dx,dy (units of grid motion),cost of move
        self.motion = [[1, 0, 1],
                  [0, 1, 1],
                  [-1, 0, 1],
                  [0, -1, 1],
                  [-1, -1, round(math.sqrt(2),3)],
                  [-1, 1, round(math.sqrt(2),3)],
                  [1, -1, round(math.sqrt(2),3)],
                  [1, 1, round(math.sqrt(2),3)]]

        # obstacle map generation
        self.obstacleMap = self.createObstacleMap()

    def createObstacleMap(self):
        obstacleMap = [[0 for i in range(self.gridX)] for j in range(self.gridY)]
        for obstacle in self.obs:
            if obstacle["type"] == "line":
                gridPoints = self.convertLineToGridPixels(obstacle)
                for point in gridPoints:
                    obstacleMap[point[0]][point[1]] = 1
        print("obstacleMap ",obstacleMap)
        return obstacleMap

    def convertLineToGridPixels(self,line):
        # Given end points of line
        lineX1 = line["left"] + line["x1"]
        lineY1 = line["top"] + line["y1"]
        lineX2 = line["left"] + line["x2"]
        lineY2 = line["top"] + line["y2"]
        minX = min(lineX1,lineX2)
        maxX = max(lineX1,lineX2)
        minY = min(lineY1,lineY2)
        maxY = max(lineY1,lineY2)
        lineGridMinX,lineGridMinY = self.convertPos(minX,minY)
        lineGridMaxX,lineGridMaxY = self.convertPos(maxX,maxY)
        gridPoints = []
        for x in range(lineGridMinX,lineGridMaxX):
            for y in range(lineGridMinY,lineGridMaxY):
                gridPoints.append((x,y))
        print("gridPoints for line", gridPoints)
        return gridPoints

    def convertPos(self,x,y):
        # Convert from pixel space to grid space

        # Ratio of self.goalX/self.width = indX/x
        indX = round(x*self.gridX/self.width)
        indY = round(y*self.gridY/self.height)
        return (indX,indY)

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
            # print(stack)
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
                    if visited[nextCell[1]][nextCell[0]] == 0 and self.obstacleMap[nextCell[1]][nextCell[0]] == 0:
                        #insert into stack, keeping stack ordered in terms of distance 
                        # print("Next Cell: ", nextCell,"GridX",self.gridX,"GridY",self.gridY,"Check visited: ",visited[nextCell[0]])
                        
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
            finalPath.reverse()

        return orderOfVisit,finalPath
                        


# if __name__ == "__main__":
#     insertion = (1,(2,0))
#     stack = [(3,(1,2)), (2,(1,1)), (1,(1,0))]
#     stack = PathFinder.binaryInsert(insertion,stack,0,len(stack))
#     print(stack)
#     stack = PathFinder.binaryInsert(insertion,stack,0,len(stack))
#     print(stack)

        
    
