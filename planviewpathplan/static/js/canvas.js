const canvas = document.getElementById('canvas1');
// const load = document.getElementById('loadBtn');
const save = document.getElementById('saveBtn');
const ctx = canvas.getContext("2d");
canvas.height = window.innerHeight;
canvas.width = window.innerWidth;
let painting = false;
if (dataURL){
    console.log(dataURL);
    var img = new Image;
    img.onload = function(){
        ctx.drawImage(img,0,0);
    };
    img.src = dataURL;
}


// load.addEventListener('click',function(){

// })

save.addEventListener('click',function(){
    const dataURL = canvas.toDataURL();
    const data = new FormData();
    data.append('canvas',dataURL);
    // const data = JSON.stringify(dataURL);
    console.log(data);
    
    const request = new XMLHttpRequest();
    request.open('POST','/save')
    request.send(data);
})

window.addEventListener('resize',function(){
    canvas.height = window.innerHeight;
    canvas.width = window.innerWidth;
})

const mouse = {
    x: undefined,
    y: undefined
}
canvas.addEventListener('click',function(event){
    mouse.x = event.offsetX;
    mouse.y = event.offsetY;
})
canvas.addEventListener('mousemove',function(event){
    mouse.x = event.offsetX;
    mouse.y = event.offsetY;
    drawCircle()
})

function drawCircle(){
    if(!painting) return;
    ctx.fillStyle = "white";
    ctx.strokeStyle = "red";
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.arc(mouse.x,mouse.y,50,0,2*Math.PI);
    ctx.stroke()
    ctx.fill()
}



function startPaint(){
    painting = true;
    drawCircle()
}
function finishedPaint(){
    painting = false;
    ctx.beginPath()
}
// function draw(){
//     if(!painting) return;
//     console.log("Paint");
//     ctx.lineWidth = 3;
//     ctx.lineCap = "round";
//     ctx.lineColor

//     ctx.lineTo(mouse.x,mouse.y);
//     ctx.stroke();
//     ctx.beginPath();
//     ctx.moveTo(mouse.x,mouse.y);
// }
//Event listeners
canvas.addEventListener('mousedown',startPaint);
canvas.addEventListener('mouseup',finishedPaint);

console.log(ctx);

// window.addEventListener("load",() =>{
//     const canvas = document.querySelector('#canvas');
//     const ctx = canvas.getContext("2d");
//     // ctx.fillRect(50,50,100,100);

//     let painting = false;
    
//     function startPaint(){
//         painting = true;
//         draw(e)
//     }
//     function finishedPaint(){
//         painting = false;
//         ctx.beginPath()
//     }
//     function draw(e){
//         if(!painting) return;
//         ctx.lineWidth = 3;
//         ctx.lineCap = "round";
//         ctx.lineColor

//         ctx.lineTo(e.clientX,e.clientY);
//         ctx.stroke();
//         ctx.beginPath();
//         ctx.moveTo(e.clientX,e.clientY);
//     }
//     //Event listeners
//     canvas.addEventListener('mousedown',startPaint);
//     canvas.addEventListener('mouseup',finishedPaint);
//     canvas.addEventListener('mousemove',draw);
// })


// var slider = document.getElementById("myRange");
// var output = document.getElementById("demo");
// output.innerHTML = slider.value; // Display the default slider value

// // Update the current slider value (each time you drag the slider handle)
// slider.oninput = function() {
//   output.innerHTML = this.value;
// }
