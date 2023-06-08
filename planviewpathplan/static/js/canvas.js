// When document is ready
var width
var height
var left
var canvas
var state
var undoStack = []
var redoStack = []
var startObj
var goalObj

$(function() {
    width = document.getElementById("canvas_container").clientWidth
    height = document.getElementById("canvas_container").clientHeight
    left = document.getElementById("canvas_container").offsetLeft
    canvas = new fabric.Canvas("canvas1", {});
    canvas.selection = false;
    canvas.setHeight( height )
    canvas.setWidth( width )
    canvas.setWidth(500);
    canvas.setHeight(500);

    // save initial state
    saveState();
    // register event listener for user's actions
    canvas.on('object:modified', function() {
      saveState();
    });

    //Start by adding goal and start objects
    startObj = new fabric.Rect({
        name: "start",
        originX: "center",
        originY: "center",
        left: width*2/7,
        top: height/2,
        fill: 'black',
        width: 20,
        height: 20,
    })
    goalObj = new fabric.Rect({ 
        name: "goal",
        originX: "center",
        originY: "center",
        left: width*4/7,
        top: height/2,
        fill: 'green',
        width: 20,
        height: 20,
    })
    startObj.hasControls = false
    goalObj.hasControls = false
    canvas.add(startObj);
    canvas.add(goalObj);

    console.log("Start obj at: x: " + startObj.left + " y: " + startObj.top)
    console.log("Goal obj at: x: " + goalObj.left + " y: " + goalObj.top)

    // Edit objects generic functions
    canvas.toObject = (function(toObject) {
    return function() {
        return fabric.util.object.extend(toObject.call(this), 
        {height: this.height, width: this.width});
    };
    })(canvas.toObject);

    startObj.toObject = (function(toObject) {
    return function() {
        return fabric.util.object.extend(toObject.call(this), 
        {name: this.name});
    };
    })(startObj.toObject);

    goalObj.toObject = (function(toObject) {
    return function() {
        return fabric.util.object.extend(toObject.call(this), 
        {name: this.name});
    };
    })(goalObj.toObject);

});

$('html').keyup(function(e){
    if(e.keyCode == 46) {
        deleteSelectedObjectsFromCanvas();
    }
});    

function deleteSelectedObjectsFromCanvas(){
    var selection = canvas.getActiveObject();
    if (selection.type === 'activeSelection') {
        selection.forEachObject(function(element) {
            canvas.remove(element);
        });
    }
    else{
        canvas.remove(selection);
    }
    canvas.discardActiveObject();
    canvas.requestRenderAll();
}


// Check coordinates tool

function checkCoords(){
    canvas.on('mouse:down', function (e){
        var pointer = canvas.getPointer(e.e);
        console.log("Clicked on - x: " + pointer.x + " y: " + pointer.y);
    })
}

// Move tool

function move(){
    canvas.selection = true;
    canvas.hoverCursor = 'move';
    canvas.off('mouse:down');
    canvas.off('mouse:move');
    canvas.off('mouse:up');

    objectSetSelect('added-line',true)
}

// Line tool

var hold = false;
let thisLine; 
function line(){
    canvas.on('mouse:down', function (e){
        var pointer = canvas.getPointer(e.e);

        thisLine = new fabric.Line([pointer.x, pointer.y, pointer.x, pointer.y], {
            id: 'added-line',
            stroke: 'black',
            strokeWidth: 5,
            selectable: false,
            originX: "center",
            originY: "center",
            perPixelTargetFind: true,
            hasBorders: false
        });
        canvas.add(thisLine)
        canvas.requestRenderAll();
        hold = true;
    });

    canvas.on('mouse:move', function (e){ 
        if (hold){
            var pointer = canvas.getPointer(e.e)
            thisLine.set({
                x2: pointer.x,
                y2: pointer.y
            });
        }
        canvas.requestRenderAll();
    });

    canvas.on('mouse:up', function (e){
        console.log("Added line",thisLine)
        console.log("Line coordinates:",thisLine.getCoords(false))
        hold = false;
        thisLine.setCoords();
    });

    canvas.selection = false;
    canvas.hoverCursor = 'auto';
    objectSetSelect('added-line',false)
}

// Rectangle tool
        
function rectangle(){
            
    canvas.onmousedown = function (e){
        img = ctx.getImageData(0, 0, width, height);
        prevX = e.clientX - canvas.offsetLeft;
        prevY = e.clientY - canvas.offsetTop;
        hold = true;
    };
            
    canvas.onmousemove = function (e){
        if (hold){
            ctx.putImageData(img, 0, 0);
            curX = e.clientX - canvas.offsetLeft - prevX;
            curY = e.clientY - canvas.offsetTop - prevY;
            ctx.strokeRect(prevX, prevY, curX, curY);
            if (fill_value){
                ctx.fillRect(prevX, prevY, curX, curY);
            }
            canvas_data.rectangle.push({ "startx": prevX, "starty": prevY, "width": curX, "height": curY, "thick": ctx.lineWidth, "stroke": stroke_value, "stroke_color": ctx.strokeStyle, "fill": fill_value, "fill_color": ctx.fillStyle });
            
        }
    };
            
    canvas.onmouseup = function(e){
        hold = false;
    };
            
    canvas.onmouseout = function(e){
        hold = false;
    };
}

// Todo: take the current svg image -> move along svg path -> convert to series of lines -> add those lines to 
//      canvas so they can be used for object avoidance
// Flatten SVG function
function flatten(path,num){
    /*
    Num sets the resolution for this function
    */
    console.log(path)
    var l = path.getTotalLength();
    var p = path.getPointAtLength(0);
    var q = path.getPointAtLength(0);
    // var d = 'M${p.x} ${p.y}'
    for(var i = (l/num);i<=l;i+=(l/num)){
        q = path.getPointAtLength(i)
        
        thisLine = new fabric.Line([p.x, p.y, q.x, q.y], {
            id: 'added-line',
            stroke: 'black',
            strokeWidth: 5,
            selectable: false,
            originX: "center",
            originY: "center",
            perPixelTargetFind: true,
            hasBorders: false
        });
        canvas.add(thisLine)
        p = path.getPointAtLength(i);
        // d+=`L${p.x} ${p.y}`
    }
    canvas.requestRenderAll();
    // path.setAttribute("d",d+"z")
}

// Simulate tool

function simulate(){
    // Let's convert any SVG images into line objects here before simulating
    if (typeof inputImg != 'undefined'){
        console.log(typeof(inputImg.path))
        inputImg.path.toSVG()
        flatten(inputImg.toSVG(),100)
        canvas.remove(inputImg).renderAll()
    }
    var data = JSON.stringify(canvas)
    var canvasSize = JSON.stringify([width-left,height])
    $.ajax({
        type:"POST",
        url: "/simulate",
        data:{
            sim_data: data, 
            canvas_size: canvasSize
        },
        success: function(response){
            displayData(response)
        }

    })
    
    // $.post("/simulate", {sim_data: data, canvas_size: canvasSize},displayData(response))

    // Send the scale information too from pathfinder so we can set width and height of the square.
    // Must keep reference to old square and current

    // wait for data to come back and upon return if data, animate each in order of visit from nothing to colour 1
    //  then change each of those to colour 2. Once we reach the goal, go back and animate from start to finish the 
    // cubes that are in final path
    // var points = [(44, 36), (44, 37), (44, 38), (44, 39), (44, 40), (44, 41), (44, 42), (44, 43), (45, 44), (46, 45), (47, 46), (48, 47), (49, 48), (50, 48), (51, 48), (52, 48), (53, 48), (54, 48), (55, 48), (56, 48), (57, 48), (58, 48), (59, 48), (60, 48), (61, 48), (62, 48), (63, 48), (64, 48), (65, 48), (66, 48), (67, 48), (68, 48), (69, 48), (70, 48), (71, 48), (72, 48), (73, 48), (74, 48), (75, 48), (76, 48), (77, 47), (78, 46), (79, 45), (80, 44), (81, 43), (82, 42), (83, 41), (84, 40), (85, 39), (86, 38), (87, 37), (88, 36)];
    

}

function displayData(response){
    var allPaths = response["orderOfVisit"];
    var finalPath = response["finalPath"];
    var scale = response["scale"]
    var objs = [];
    var first = true;

    // for (let i=0;i<allPaths.length;i++){
    //     //How to animate this and slow it down
    //     point = allPaths[i];
    //     obj = new fabric.Rect({
    //         originX: "center",
    //         originY: "center",
    //         fill: 'blue',
    //         width: scale,
    //         height: scale,
    //         left: point[0]*scale,
    //         top: point[1]*scale,
    //         hasControls: false
    //     })
    //     canvas.add(obj);
    //     objs.push(obj);
    //     if (!first){
    //         objs[i-1].fill = 'grey';
    //     }
    //     first = false
    // }
    // startObj.bringToFront()
    goalObj.bringToFront()
    canvas.requestRenderAll();
    // console.log("DISPLAY", finalPath,scale);

    // Probably better here if we have a path object with lines between points
    finalPath.forEach(point => {
        obj = new fabric.Rect({
            originX: "center",
            originY: "center",
            fill: 'yellow',
            width: scale,
            height: scale,
            left: point[0]*scale,
            top: point[1]*scale,
            hasControls: false
        })
        canvas.add(obj);
        startObj.bringToFront()
        goalObj.bringToFront()
        canvas.requestRenderAll();
    });

}

// Load tool

// const fileInput = document.getElementById("files");
let inputImg;
function load(e){
    var url = URL.createObjectURL(e.target.files[0]);
    fabric.loadSVGFromURL(url,function(objects)
    {
        inputImg = fabric.util.groupSVGElements(objects)
        inputImg.set({
            hasBorders:true,
            hasControls:true,
            selectable:true,
        })
        console.log("Here I am:",inputImg)
        // inputImg = new fabric.Path(objects[0].d, {
        //     fill: '#333',
        //     opacity: 1,
        //     hasBorders: true,
        //     hasControls: true,
        //     hasRotatingPoint: true,
        //     selectable: true,
        //     preserveObjectStacking: true,
        //     objectCaching: false,
        // });
        canvas.add(inputImg).renderAll();


        // objects.forEach(function(svg){
        //     svg.set({
        //         left: 200,
        //         top: 200,
        //         originX: 'center',
        //         originY: 'center'
        //     });
        //     svg.scaleToWidth(200);
        //     svg.scaleToHeight(200);
        //     canvas.add(svg).renderAll()
        //     console.log(svg)
        // });
        
    //   var loadedObjects = new fabric.Group(objects);
    //   loadedObjects.set({
    //     left: 0,
    //     top: 0,
    //     width:100,
    //     height:100
    //   });
    //   canvas.add(loadedObjects);
    //   canvas.renderAll();
    });
}


// Save tool

function saveState(){
    // var filename = document.getElementById("fname").value;
    var data = JSON.stringify(canvas);
    var image = canvas.toDataURL();
    const date = new Date()
    $.post("/save", { save_fname: "file" + date.getTime().toString(), save_cdata: data, save_image: image });
    console.log("SAVED");
} 
        
// Reset tool

function reset(){
    canvas.clear()
    canvas.add(startObj)
    canvas.add(goalObj)
}

// Undo and redo tools

/**
 * Push the current state into the undo stack and then capture the current state
 */
function saveState() {
  // clear the redo stack
  redo = [];
  $('#redoBtn').prop('disabled', true); //Disable button when clicked
  // initial call won't have a state
  if (state) {
    undoStack.push(state);
    $('#undoBtn').prop('disabled', false);
  }
  state = JSON.stringify(canvas);
}

/**
 * Save the current state in the redo stack, reset to a state in the undo stack, and enable the buttons accordingly.
 * Or, do the opposite (redo vs. undo)
 * @param playStack which stack to get the last state from and to then render the canvas as
 * @param saveStack which stack to push current state into
 * @param buttonsOn jQuery selector. Enable these buttons.
 * @param buttonsOff jQuery selector. Disable these buttons.
 */
function replay(playStack, saveStack, buttonsOn, buttonsOff) {
  saveStack.push(state);
  state = playStack.pop();
  var on = $(buttonsOn);
  var off = $(buttonsOff);
  // turn both buttons off for the moment to prevent rapid clicking
  on.prop('disabled', true);
  off.prop('disabled', true);
  canvas.clear();
  canvas.loadFromJSON(state, function() {
    canvas.renderAll();
    // now turn the buttons back on if applicable
    on.prop('disabled', false);
    if (playStack.length) {
      off.prop('disabled', false);
    }
  });
}

function undo(){
    replay(undoStack, redoStack, '#redoBtn', '#undoBtn');
}
function redo(){
    replay(redoStack, undoStack, '#undoBtn', '#redoBtn');
}


// Form tools

function openForm() {
    document.getElementById("myModal").classList.add('show')
  }
  
function closeForm() {
    document.getElementById("myModal").classList.remove('show')
}

// helpers

function objectSetSelect(id,value){
    canvas.getObjects().forEach(o => {
        if (o.id === id){
            o.set({
                selectable: value
            });
        }
    });
}   
