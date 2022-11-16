// import {fabric} from "../../node_modules/fabric/dist/fabric.js";
// import {fabric} from "C:\Users\conor\Documents\CodingProjects\Robotic Path Planner\node_modules\fabric\dist\fabric.js";
// const fabric = require("fabric"); //Node.JS is a server-side technology, not a browser technology. Thus, Node-specific calls, like require(), do not work in the browser.
var width  = Math.max(document.documentElement.clientWidth,  window.innerWidth  || 0);
var height = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

var canvas = new fabric.Canvas("canvas1", {});

canvas.setHeight( height )
canvas.setWidth( width )

//Start by adding goal and start objects
var startObj = new fabric.Rect({
    name: "start",
    originX: "center",
    originY: "center",
    left: width*2/7,
    top: height/2,
    fill: 'black',
    width: 20,
    height: 20,
})
var goalObj = new fabric.Rect({ 
    name: "goal",
    originX: "center",
    originY: "center",
    left: width*4/7,
    top: height/2,
    fill: 'green',
    width: 20,
    height: 20,
})
canvas.add(startObj);
canvas.add(goalObj);

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

var hold = false;

// Move tool

canvas.selection = false;
function move(){
    canvas.selection = true;
    canvas.hoverCursor = 'move';
    canvas.off('mouse:down');
    canvas.off('mouse:move');
    canvas.off('mouse:up');

    objectSetSelect('added-line',true)
}

// Line tool

let thisLine; 
function line(){
    canvas.on('mouse:down', function (e){
        var pointer = canvas.getPointer(e.e);

        thisLine = new fabric.Line([pointer.x, pointer.y, pointer.x, pointer.y], {
            id: 'added-line',
            stroke: 'black',
            strokeWidth: 3,
            selectable: false,
            originX: "center",
            originY: "center",
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
         hold = false;
         thisLine.setCoords();
    });

    canvas.selection = false;
    canvas.hoverCursor = 'auto';
    objectSetSelect('added-line',false)
}

// Simulate tool

function simulate(){
    var data = JSON.stringify(canvas);
    var canvasSize = JSON.stringify([width,height])
    // var height = JSON.stringify(height);
    // var width = JSON.stringify(width);
    $.post("/simulate", {sim_data: data, canvas_size: canvasSize});
    console.log("Simulated data",data,height,width);
}

// Save tool

function save(){
    // var filename = document.getElementById("fname").value;
    var data = JSON.stringify(canvas);
    var image = canvas.toDataURL();
    const date = new Date()
    $.post("/save", { save_fname: "file" + date.getTime().toString(), save_cdata: data, save_image: image });
    console.log("SAVED");
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
        

// var save = document.getElementById('saveBtn');
// var ctx = canvas.getContext("2d");

// // var lineWidthHolder = document.getElementById('lineThicknessSlider')
// canvas.height = window.innerHeight;
// canvas.width = window.innerWidth;
// var width = canvas.width;
// var height = canvas.height;
// var curX, curY, prevX, prevY;

// // ctx.lineWidth = lineWidthHolder.value;
// var fill_value = true;
// var stroke_value = false;
// var canvas_data = {"pencil": [], "line": [], "rectangle": [], "circle": [], "eraser": []}
// ctx.fillStyle = "white";
// ctx.strokeStyle = "red";                     

// window.addEventListener('resize',function(){
//     canvas.height = window.innerHeight;
//     canvas.width = window.innerWidth;
// })
        
// function fill(){
//     fill_value = true;
//     stroke_value = false;
// }
        
// function outline(){
//     fill_value = false;
//     stroke_value = true;
// }
               
// function reset(){
//     ctx.clearRect(0, 0, canvas.width, canvas.height);
//     canvas_data = { "pencil": [], "line": [], "rectangle": [], "circle": [], "eraser": [] }
// }
        
// // pencil tool
        
// function pencil(){
        
//     canvas.onmousedown = function(e){
//         curX = e.clientX - canvas.offsetLeft;
//         curY = e.clientY - canvas.offsetTop;
//         // curX = e.offsetX;
//         // curY = e.offsetY;
//         hold = true;
            
//         prevX = curX;
//         prevY = curY;
//         ctx.beginPath();
//         ctx.moveTo(prevX, prevY);
//     };
        
//     canvas.onmousemove = function(e){
//         if(hold){
//             curX = e.clientX - canvas.offsetLeft;
//             curY = e.clientY - canvas.offsetTop;
//             draw();
//         }
//     };
        
//     canvas.onmouseup = function(e){
//         hold = false;
//     };
        
//     canvas.onmouseout = function(e){
//         hold = false;
//     };
        
//     function draw(){
//         ctx.lineTo(curX, curY);
//         ctx.stroke();
//         canvas_data.pencil.push({ "startx": prevX, "starty": prevY, "endx": curX, "endy": curY, "thick": ctx.lineWidth, "color": ctx.strokeStyle });
//     }
// }
        
// // line tool

    // prevX = e.clientX - canvas.offsetLeft;
    // prevY = e.clientY - canvas.offsetTop;

    // if (hold){

    //     ctx.putImageData(img, 0, 0);
    //     curX = e.clientX - canvas.offsetLeft;
    //     curY = e.clientY - canvas.offsetTop;
    //     ctx.beginPath();
    //     ctx.moveTo(prevX, prevY);
    //     ctx.lineTo(curX, curY);
    //     ctx.stroke();
    //     canvas_data.line.push({ "startx": prevX, "starty": prevY, "endx": curX, "endY": curY, "thick": ctx.lineWidth, "color": ctx.strokeStyle });
    //     ctx.closePath();
    // }

// // rectangle tool
        
// function rectangle(){
            
//     canvas.onmousedown = function (e){
//         img = ctx.getImageData(0, 0, width, height);
//         prevX = e.clientX - canvas.offsetLeft;
//         prevY = e.clientY - canvas.offsetTop;
//         hold = true;
//     };
            
//     canvas.onmousemove = function (e){
//         if (hold){
//             ctx.putImageData(img, 0, 0);
//             curX = e.clientX - canvas.offsetLeft - prevX;
//             curY = e.clientY - canvas.offsetTop - prevY;
//             ctx.strokeRect(prevX, prevY, curX, curY);
//             if (fill_value){
//                 ctx.fillRect(prevX, prevY, curX, curY);
//             }
//             canvas_data.rectangle.push({ "startx": prevX, "starty": prevY, "width": curX, "height": curY, "thick": ctx.lineWidth, "stroke": stroke_value, "stroke_color": ctx.strokeStyle, "fill": fill_value, "fill_color": ctx.fillStyle });
            
//         }
//     };
            
//     canvas.onmouseup = function(e){
//         hold = false;
//     };
            
//     canvas.onmouseout = function(e){
//         hold = false;
//     };
// }
        

// function save(){
//     var data = JSON.stringify(canvas);

// }

