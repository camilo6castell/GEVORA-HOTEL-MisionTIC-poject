function validarFormulario(event){
    let user = document.getElementById("user");
    let pass = document.getElementById("pass");
    let formato_email = /^\w+([\.-]?\w+)@\w+([\.-]?\w+)(\.\w{2,3})+$/;

    if (!user.value.match(formato_email)) {
      alert("Debes ingresar un email electronico valido!");
      event.preventDefault();
      user.focus();      
    }
    let passL = pass.value.length;
    if (passL == 0 || passL < 8) {
        alert("Debes ingresar una password con mas de 8 caracteres");
        event.preventDefault();
        pass.focus();
        return false;
    }
}

function mostrarPassword(){    
    obj.type = "text";
  }
function ocultarPassword(){
    obj.type="password"
}

/* Validacion form */

let log_in_form = document.getElementById("log_in_form");

log_in_form.addEventListener("submit", validarFormulario);

/* Mostras/ocultar password */

let imagen = document.querySelector("#showpass");
let obj = document.getElementById("pass");

imagen.addEventListener("mouseover", mostrarPassword);
imagen.addEventListener("mouseout", ocultarPassword);