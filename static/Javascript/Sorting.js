

function Clear(){
        location.reload();
        return false;
}

let num_array = [];
function generateArray(min,max,elements_number) {
    //Remove pre existing <div> tags before creating new ones by removing the innerhtml of our container
    document.getElementById("array").innerHTML = '';
    num_array = [];
    for(let i =0;i<elements_number;i++){
        let num = randomIntFromInterval(min,max);
        while (num_array.includes(num)) {
            num = randomIntFromInterval(min,max);
        }
        num_array.push(num)
    }
  $(document).ready(function () {
    for (let i = 0; i < elements_number; i++) {
        let color = "rgb("+(num_array[i]*5 + 150).toString() +','+(num_array[i]*2 + 100).toString() +',' +(num_array[i]).toString() + ');';
        let style = "style='float: left;background-color:"+color+"height:" +(num_array[i] + 40).toString()+"px;"+"border: 1px solid;'";
        let id = " id='"+num_array[i].toString()+"' "
        $("#array").append("<div"+id+style+">"+num_array[i]+" </div>");
    }

});
}

$(document).ready(function() {

        $('form').on('submit', function(event) {
       $.ajax({
          type: "POST",
          contentType: "application/json;charset=utf-8",
          url: "/SortArray",
          traditional: "true",
          data: JSON.stringify([num_array,changeSelect()]),
          dataType: "json"
          })
        .done(function(data) {


            let timeout = output.innerHTML;
            //works recursively in the same way that we draw in pathfinding.js
            // while i < swaps.lenght ----> the if clause
            // we  increase i by one and call test on itself

            let swaps = JSON.parse(data.output);
            console.log(swaps);
            let i =0;
            function test(){
            setTimeout(function () {
                timeout = output.innerHTML;

                 if(i < swaps.length){
                  draw(swaps[i][0],swaps[i][1])}
                  i++;
                 test();

            },150 - timeout);}
            test();

      });
      event.preventDefault();
      });
});



function changeSelect() {
    let selectTag = document.getElementById("algorithm");
    let choice = selectTag.options[selectTag.selectedIndex].value;
    alert(choice);
    return choice
}




function draw(index1,index2) {
        let temp = num_array[index1];
        num_array[index1] = num_array[index2];
        num_array[index2] = temp;

        let div1 = document.getElementById(num_array[index1].toString());
        let div2 = document.getElementById(num_array[index2].toString());
        //div1.classList.add("test");
        let temp2_style = div1.style.cssText;
        let temp3_innerHTML = div1.innerHTML;
        let temp4 = div1.id;

        div1.id = div2.id;
        div1.style.cssText = div2.style.cssText;
        div1.innerHTML = div2.innerHTML;
        div2.id = temp4;
        div2.style.cssText = temp2_style;
        div2.innerHTML = temp3_innerHTML;

}

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}

