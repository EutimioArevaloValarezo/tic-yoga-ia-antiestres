$(document).ready(function () {

    // Al cambiar la rutina seleccionada, cargar las posturas
    $('#rutina-select').change(function () {
        var rutinaId = $(this).val();
        console.log(rutinaId)
        $.ajax({
            url: '/rutina/' + rutinaId,
            method: 'GET',
            dataType: 'json',
            success: function (rutina) {
                // console.log(rutina);
                var posturasContainer = document.getElementById('posturas-container');
                posturasContainer.innerHTML = '';
                rutina.forEach(postura => {
                    var posturaHtml = `
                        <div class="col-md-12 mt-2">
                            <div class="row g-0">
                                <div class="col-md-2">
                                    <img src="../static/images/${postura.index_modelo}.png" class="img-fluid rounded-start w-100" style="height: 200px; object-fit: contain;" alt="${postura.nombre}">
                                </div>
                                <div class="col-md-10">
                                    <div class="card-body">
                                        <h5 class="card-title">${postura.nombre}</h5>
                                        <p class="card-text">${postura.descripcion}</p>
                                        <p class="card-text"><small class="text-body-secondary">${postura.categoria}</small></p>
                                    </div>
                                </div>
                            </div>
                        </div>`;

                    posturasContainer.innerHTML += posturaHtml;
                });
            }
        });

    });
});
