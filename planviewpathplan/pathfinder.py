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
        self.start = (round(start[0]),round(start[1]))
        self.goal = (round(goal[0]),round(goal[1]))
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
                  [0, -1, 1],
                  [-1, -1, 2],
                  [-1, 1, 2],
                  [1, -1, 2],
                  [1, 1, 2]]

        # get the required coordinates for each line
        self.lineCoords = []
        for obstacle in self.obs:
            print(obstacle["type"])
            if obstacle["type"] == "line":
                self.createlineCoords(obstacle)
            elif obstacle["type"] == "path":
                # What to do if we have a path from an svg
                for line in obstacle["path"]:
                    print(line)
                
            
    def createlineCoords(self,line):
        #First find the corners of the line
        x1, y1 = line["left"] + line["x1"],line["top"] + line["y1"] 
        x2, y2 = line["left"] + line["x2"],line["top"] + line["y2"]
        lineAngle = math.atan2(y2-y1,x2-x1)
        xShift = math.sin(lineAngle)*line["strokeWidth"]/2*5
        yShift = math.cos(lineAngle)*line["strokeWidth"]/2*5
        if y2-y1 < 0:
            p1 = [x1 - xShift,y1 + yShift]
            p2 = [x1 + xShift,y1 - yShift]
            p3 = [x2 - xShift,y2 + yShift]
        else:
            p1 = [x1 + xShift,y1 - yShift]
            p2 = [x1 - xShift,y1 + yShift]
            p3 = [x2 + xShift,y2 - yShift]
        self.lineCoords.append((np.array(p1),np.array(p2),np.array(p3)))
        
    def isCollision(self,point,line):
        p12 = line[1]-line[0]
        p1M = point-line[0] 
        p13 = line[2]-line[0]
        return 0 < np.dot(p1M,p12) < np.dot(p12,p12) and 0 < np.dot(p1M,p13) < np.dot(p13,p13)
        
    def binaryInsert(self,element,stack,left,right):
        """Binary Insertion of element into stack, descending, based on distance from tuple (distance,current,prev)
        
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
        
    def distHeuristicCalc(self,current):
        return (self.goal[1] - current[1])**2 + (self.goal[0] - current[0])**2   

    def findPath(self):
        """
        Using A* search algorithm, with heuristic calculated as squared distance from goal
        
        output:
            searchPath: a list of points that were searched, in order
            finalPath: a list of points for the final shortest path to the goal, in order
        """
        # Go in each direction in self.motion, keeping track of cost. 
        # Keep the list of points as they are visited. A greedy approach where we assume that the best next step
            # taken until the end will give the optimal solution at the end
        # At the end, when we have the shortest path (least cost), save all the points taken to get to goal
        # Can add cell if not in visited and not colliding with line
        foundGoal = False
        visited = [[0 for i in range(self.gridX)] for j in range(self.gridY)]
        orderOfVisit = [self.start] #Here we just add the cells as we visit them
        prevNodes = dict() #current:previous
        stack = [(self.distHeuristicCalc(self.start),self.start)] # (Distance travelled + distance heuristic,cur pos)
        print("Start",self.start,"Goal",self.goal)
        while not foundGoal and stack:
            curDistance,curCell = stack.pop()
            for move in self.motion:
                nextX = curCell[0] + move[0]
                nextY = curCell[1] + move[1]
                if 0 <= nextX < self.gridX and 0 <= nextY < self.gridY:
                    nextCell = (nextX,nextY)
                    if nextCell == self.goal:
                        prevNodes[self.goal] = curCell
                        foundGoal = True
                        break
                    if visited[nextCell[1]][nextCell[0]] == 0:
                        visited[nextCell[1]][nextCell[0]] = 1
                        orderOfVisit.append(nextCell)
                        prevNodes[nextCell] = curCell
                        pnt = np.array([nextX,nextY])
                        collision = False
                        for line in self.lineCoords:
                            if self.isCollision(pnt,line):
                                collision = True
                                break
                        if not collision:
                            curHeuristic = self.distHeuristicCalc(curCell)
                            nextHeursitc = self.distHeuristicCalc(nextCell)
                            toInsert = (curDistance - curHeuristic + move[2] + nextHeursitc,nextCell)
                            stack = self.binaryInsert(toInsert,stack,0,len(stack))
                        
        finalPath = []
        if foundGoal:
            #Then we need to trace back and form our list of points that make up the goal
            currentNode = self.goal
            while currentNode!=self.start:
                finalPath.append(currentNode)
                currentNode = prevNodes[currentNode]
            finalPath.append(self.start)
            finalPath.reverse()
        # print("Path found!",finalPath)
        return orderOfVisit,finalPath

        
    
