
let success= document.querySelector('.success');
let error = document.querySelector('.error');

if (error.textContent !== ""){
success.style.visibilty('hidden');
error.style.visibilty('visible');
console.log("error detect")
}
else{
    success.style.visibilty('visible');
    error.style.visibilty('hidden');
    console.log("no error ")
}
// ?