 //   var css = 'table td:hover{ background-color: #00ff00 }';

function clearGraph(){
        location.reload();
        return false;
}
    let create_walls = false;
    let walls = [];
    let startCellID = null;
    let endCellID = null;
    let pick_start_point = false;
    let picked_start = false;
    //picks the start/end point based ont he boolean values.If the button hasnt been clicked at all
    // the variables are false then pick_start/end_point becomes true and we get to pick a point.
    //We then use the id of that point to do the required actions.
    //Click again the button for picking an end/start point will remove the previously
    //selected point
    function pickStartPoint(){

        if(pick_start_point == false && picked_start == false){
            pick_start_point = true;
            if ( document.getElementById(startCellID).classList.contains('start') ){
            document.getElementById(startCellID).classList.remove('start');}
            names = []
        }
        else if (picked_start){
            pick_start_point = false;
            picked_start = false;
            if ( document.getElementById(startCellID).classList.contains('start') ){
            document.getElementById(startCellID).classList.remove('start');}

        }
    }
    let pick_end_point = false;
    let picked_end = false;
    function pickEndPoint() {

          if(pick_end_point == false && picked_end == false){
            pick_end_point = true;
            if ( document.getElementById(endCellID).classList.contains('end') ){
            document.getElementById(endCellID).classList.remove('end');}

        }
        else if (picked_end){
            pick_end_point = false;
            picked_end = false;
            if ( document.getElementById(endCellID).classList.contains('end') ){
            document.getElementById(endCellID).classList.remove('end');}
            document.getElementById(endCellID).classList.add('cell');

        }
    }

    //to check if our mouse is down or up
 //when the mouse is down the mouseDown variable is 1
 //when its up mouseDown is 0
 let stop_walls = false;
 let mouseDown = 0;

    document.onmousedown = function () {
        ++mouseDown;

 }
  document.onmouseup = function () {
        if(stop_walls){
            create_walls = false;
        }
        --mouseDown;
 }




      //On submit with an ajax request get from Flask the information returned from
    //dijkstras algorithm and the shortest path
      $(document).ready(function() {
        $('form').on('submit', function(event) {
       $.ajax({
          type: "POST",
          contentType: "application/json;charset=utf-8",
          url: "/runAlgo",
          traditional: "true",
          data: JSON.stringify([startCellID,endCellID,walls]),
          dataType: "json"
          })
        .done(function(data) {
            let timeout = output.innerHTML;
          //$('#output').text(data.output).show();
          // lists contains two sublists. In index 0 all the neighbors in sorted order. In index 1 the shortest path.
          let lists = JSON.parse(data.output);
          let neighbors = lists[0];
          let shortestPath = lists[1];
            console.log(neighbors)
          var i = 0;
          var finishedNeighbors = false;
          var j = 0;
          //Draw the nodes.
            function draw(){
              setTimeout(function () {
                  timeout = output.innerHTML;
                  console.log(lists[i])
                  if(neighbors[i] != endCellID){
                  document.getElementById(neighbors[i]).classList.add('neighbor');}
                  else finishedNeighbors = true;

                  i++;
                  if(i<neighbors.length){
                      draw();
                  }else drawPath();
              },150 - timeout )
          }
          draw();
          function drawPath(){
              setTimeout(function () {
                 // console.log(lists[i])
                  if(shortestPath[j] != endCellID && shortestPath[j]!= startCellID){
                  document.getElementById(shortestPath[j]).classList.add('path');}

                  j++;
                  if(j<shortestPath.length){
                      drawPath();
                  }
              },75)
          }
          console.log(neighbors)











      });
      event.preventDefault();
      });
});

    function addWalls(){
        create_walls = true;

    }

    $(document).on('click', '.cell', function ( event ) {
        if(pick_start_point == true){
            var startPoint = document.getElementById(event.target.id);
            startCellID = event.target.id;


            document.getElementById(startCellID).classList.add('start');
            pick_start_point = false;
            picked_start = true;
            console.log(startCellID)
        }
        if (pick_end_point == true){
            var endPoint = document.getElementById(event.target.id);
            endCellID = event.target.id;

            document.getElementById(endCellID).classList.add('end');
            pick_end_point = false;
            picked_end = true;
            console.log(endCellID)
        }
    $( "#log" ).html( "clicked: " + event.target.id );
});

//Listener on mouseover for cells
// once the boolean create_walls == true
// dragging our mouse over cells while the mouse is down will cause
// the cells to become walls.

    $(document).on("mouseover", '.cell', function ( event ) {
        if (mouseDown && create_walls){
        //after we have clicked on create walls and tried to create at least one
        //if we let the mouse up then we stop creating walls
        stop_walls = true;
        let CellID = event.target.id;
        document.getElementById(CellID).classList.add('wall');
        walls.push(CellID);}
        // if the mouse is up after create walls

        //console.log(CellID);

    $( "#log" ).html( "clicked: " + event.target.id );
});



