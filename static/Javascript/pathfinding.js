 //   var css = 'table td:hover{ background-color: #00ff00 }';


function clearGraph(){
        location.reload();
        return false;
}
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




      //On submit with an ajax request get from Flask the information returned from
    //dijkstras algorithm and the shortest path
      $(document).ready(function() {
        $('form').on('submit', function(event) {
       $.ajax({
          type: "POST",
          contentType: "application/json;charset=utf-8",
          url: "/runAlgo",
          traditional: "true",
          data: JSON.stringify([startCellID,endCellID]),
          dataType: "json"
          })
        .done(function(data) {
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

          function draw(){
              setTimeout(function () {
                  console.log(lists[i])
                  if(neighbors[i] != endCellID){
                  document.getElementById(neighbors[i]).classList.add('neighbor');}
                  else finishedNeighbors = true;

                  i++;
                  if(i<neighbors.length){
                      draw();
                  }else drawPath();
              },15)
          }
          draw();









      });
      event.preventDefault();
      });
});

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
