function generateArray(min,max,elements_number) {

    if(!!document.getElementById("Arrcontainer")){
        document.body.removeChild(document.getElementById("Arrcontainer"));
    }
    let index;
    let table = document.createElement('table');
    let div_container = document.createElement('div');
    div_container.id = "Arrcontainer";
    div_container.classList.add("array-container")
    let num_array = [];

     for (index = 0; index < elements_number;index++){
         num_array.push(randomIntFromInterval(min,max));
     }


    for (index = 0; index < elements_number;index++){

        var td1 = document.createElement('td');
        td1.style.border = "2px solid";
        td1.backgroundColor ="red";
        td1.style.height = index.toString()+"px";

        var text1 = document.createTextNode( num_array[index]);
        td1.appendChild(text1);
        table.appendChild(td1);
    }
    div_container.appendChild(table)
    document.body.appendChild(div_container);

}

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}