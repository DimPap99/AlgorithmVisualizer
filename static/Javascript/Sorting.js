function generateArray(min,max,elements_number) {
    //Remove pre existing divs before creating new ones
    document.getElementById("array").innerHTML = '';
    let num_array = [];
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
        let style = "style='float: left;background-color:"+color+"height:" +(num_array[i] + 25).toString()+"px;"+"border: 1px solid;'";
        let id = " id='"+num_array[i].toString()+"' "

        $("#array").append("<div"+id+style+">"+num_array[i]+" </div>");
    }



});


}

function test() {
   let div = document.getElementById("1");
   div.style.height = "100px";

   alert(div);

}

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}