$(document).ready(function () {
    $('.btn.btn-info').click(function () {
        var identificador = $(this).data('id');
        $.ajax({
            type: 'POST',
            url: '/get_administrador',
            data: { 'id_admin': identificador },
            success: function (response) {
                var usuario = response.usuario;
                $('#res_usuario').text(usuario);
                $('#id_res_usuario').attr('value', identificador);
            },
            error: function (error) {
                console.log('Error en la solicitud Ajax:', error);
            }
        });
    });

    $('.btn.btn-danger').click(function () {
        var identificador = $(this).data('id');
        console.log(identificador)
        $.ajax({
            type: 'POST',
            url: '/get_administrador',
            data: { 'id_admin': identificador },
            success: function (response) {
                var usuario = response.usuario;
                $('#del_usuario').text(usuario);
                $('#id_del_usuario').attr('value', identificador);
            },
            error: function (error) {
                console.log('Error en la solicitud Ajax:', error);
            }
        });
    });
});

$('form[name=agregar_administrador]').submit(function (e) {
    var $form = $(this);
    var data = $form.serialize();
    var $alert = $form.find('.alert');
    $.ajax({
        url: '/agregar_administrador',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function (resp) {
            // $alert.text(resp.success).removeClass('visually-hidden');
            window.location.href = '/admin/gestionar_administradores'
        },
        error: function (resp) {
            console.log(resp);
            $alert.text(resp.responseJSON.error).removeClass('visually-hidden');
        }

    });

    e.preventDefault();
});