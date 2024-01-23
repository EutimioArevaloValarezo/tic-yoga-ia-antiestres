var socket = io();

function cuentaRegresiva(tiempo, titulo) {
    document.querySelector('h1').innerText = titulo;
    var voice = new Audio('../static/voice/'+titulo+'.mp3');
    voice.play()
    return new Promise((resolve, reject) => {
        let intervalo = setInterval(() => {

            document.querySelector('h2').innerText = tiempo;
            tiempo--;
            if (tiempo < 0) {
                clearInterval(intervalo);
                resolve();
            }
        }, 1000);
    });
}

// Función para cerrar el modal de Bootstrap
function cerrarModal() {
    $('#my-modal').modal('hide');
}

// Ejecutar las cuentas regresivas en orden
async function ejecutarCuentasRegresivas(inhalar, retener, exhalar, repeticiones) {
    await cuentaRegresiva(inhalar, 'Inhalar');
    await cuentaRegresiva(retener, 'Retener');
    await cuentaRegresiva(exhalar, 'Exhalar');
    cerrarModal();
}

socket.on('pose_update', function (data) {
    document.getElementById('pose_image').src = '../static/images/posturas/' + data.pose_index + '.png';
});

socket.on('precision_update', function (data) {
    document.querySelector('#idPresicion').textContent = data.precision + '%';
});

socket.on('redireccion', function (data) {
    window.location.href = window.location.origin+data.ruta
});

socket.on('pop_up', function (data) {
    $('#my-modal').modal('show');
    
    ejecutarCuentasRegresivas(data.inhalar, data.retener, data.exhalar);
});

socket.on('precision_update', function (data) {
    document.querySelector('#idTiempoRespiracion').textContent = data.tiempo_respiracion;
});

