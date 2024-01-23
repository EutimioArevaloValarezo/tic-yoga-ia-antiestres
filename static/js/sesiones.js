$(document).ready(function () {
    $('.btn.btn-info').click(function () {
        var id_pymongo = $(this).data('id');
        console.log(id_pymongo)
        $.ajax({
            type: 'POST',
            url: '/generar_estaditica',
            data: { 'id_pymongo': id_pymongo },
            success: function (response) {
                var ruta_imagen = response.ruta_imagen;
                // Añade un parámetro de consulta con un valor único (sello de tiempo)
                ruta_imagen += '?t=' + new Date().getTime();
                $('#estadisticaGrafica').attr('src', ruta_imagen);
            },
            error: function (error) {
                console.log('Error en la solicitud Ajax:', error);
            }
        });
    });

    $('.btn.btn-success').click(function () {
        var id_pymongo = $(this).data('id');
        var clases = $('#alert_obs').attr('class');
        console.log(clases);
        if (!$('#alert_obs').hasClass('visually-hidden')) {
            $('#alert_obs').addClass('visually-hidden');
        }
        $.ajax({
            type: 'POST',
            url: '/get_observacion',
            data: { 'idObservacion': id_pymongo },
            success: function (response) {
                var text_observacion = response.text_observacion;
                $('#idObsTextarea').val(text_observacion);
                $('#hiddenId').attr('value', id_pymongo);
            },
            error: function (error) {
                console.log('Error en la solicitud Ajax:', error);
            }
        });
    });
});

$('form[name=observacionFrom]').submit(function (e) {
    var $form = $(this);
    var data = $form.serialize();
    var $alert = $form.find('.alert');
    $.ajax({
        url: '/editar_observacion',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function (resp) {
            // window.location.href = '/'
            $alert.removeClass('visually-hidden');
        },
        error: function (resp) {
            console.log(resp);
        }

    });

    e.preventDefault();
});